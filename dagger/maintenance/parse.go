package main

import (
	"cmp"
	"context"
	"fmt"
	"slices"

	"github.com/hashicorp/hcl/v2"
	"github.com/hashicorp/hcl/v2/hclsimple"
	"github.com/zclconf/go-cty/cty"

	"dagger/maintenance/internal/dagger"
)

// buildMatrix is the set of distribution/PG-major combinations to build.
// It holds explicit pairs (rather than two independent lists), so each distribution
// can declare its own set of PG majors.
type buildMatrix struct {
	Combinations []buildCombo
}

// buildCombo is a single distribution + PG major combination to build.
type buildCombo struct {
	Distribution string
	MajorVersion string
}

// hasDistribution reports if given a distribution is present in a buildMatrix.
func (m *buildMatrix) hasDistribution(distribution string) bool {
	return slices.ContainsFunc(m.Combinations, func(combo buildCombo) bool {
		return combo.Distribution == distribution
	})
}

// contains reports if a given distribution/major pair is present in a buildMatrix.
func (m *buildMatrix) contains(distribution, majorVersion string) bool {
	return slices.ContainsFunc(m.Combinations, func(combo buildCombo) bool {
		return combo.Distribution == distribution && combo.MajorVersion == majorVersion
	})
}

type extensionVersion struct {
	Package string `hcl:"package" cty:"package"`
}

type versionMap map[string]map[string]extensionVersion

type extensionMetadata struct {
	// BuildSystem is optional for existing targets. An omitted value is the
	// historical Debian build path; pgrx targets opt in explicitly so the
	// existing Debian workflows cannot accidentally schedule them.
	BuildSystem            string            `hcl:"build_system,optional"`
	Name                   string            `hcl:"name" cty:"name"`
	SQLName                string            `hcl:"sql_name" cty:"sql_name"`
	ImageName              string            `hcl:"image_name" cty:"image_name"`
	SharedPreloadLibraries []string          `hcl:"shared_preload_libraries" cty:"shared_preload_libraries"`
	PostgresqlParameters   map[string]string `hcl:"postgresql_parameters" cty:"postgresql_parameters"`
	ExtensionControlPath   []string          `hcl:"extension_control_path" cty:"extension_control_path"`
	DynamicLibraryPath     []string          `hcl:"dynamic_library_path" cty:"dynamic_library_path"`
	LdLibraryPath          []string          `hcl:"ld_library_path" cty:"ld_library_path"`
	BinPath                []string          `hcl:"bin_path" cty:"bin_path"`
	Env                    map[string]string `hcl:"env" cty:"env"`
	AutoUpdateOsLibs       bool              `hcl:"auto_update_os_libs" cty:"auto_update_os_libs"`
	RequiredExtensions     []string          `hcl:"required_extensions" cty:"required_extensions"`
	CreateExtension        bool              `hcl:"create_extension" cty:"create_extension"`
	Versions               versionMap        `hcl:"versions" cty:"versions"`
	Remain                 hcl.Body          `hcl:",remain"`
}

const (
	metadataFile = "metadata.hcl"
)

const (
	debianBuildSystem = "debian"
	pgrxBuildSystem   = "pgrx"
)

// effectiveBuildSystem preserves the repository's historical default while
// rejecting unknown explicit values at the target-list boundary.
func effectiveBuildSystem(metadata *extensionMetadata) (string, error) {
	if metadata.BuildSystem == "" {
		return debianBuildSystem, nil
	}
	if metadata.BuildSystem != debianBuildSystem && metadata.BuildSystem != pgrxBuildSystem {
		return "", fmt.Errorf("unsupported build_system %q for target %q", metadata.BuildSystem, metadata.Name)
	}
	return metadata.BuildSystem, nil
}

// parseBuildMatrix derives the build matrix for a target extension by reading
// its metadata.hcl from the source directory.
func parseBuildMatrix(ctx context.Context, source *dagger.Directory, target string) (*buildMatrix, error) {
	metadata, err := parseExtensionMetadata(ctx, source.Directory(target))
	if err != nil {
		return nil, err
	}

	return buildMatrixFromMetadata(metadata), nil
}

// buildMatrixFromMetadata derives the build matrix (distributions and PG majors)
// directly from the keys of the metadata.versions map, mirroring how the
// docker-bake.hcl matrix is computed.
func buildMatrixFromMetadata(metadata *extensionMetadata) *buildMatrix {
	var matrix buildMatrix
	for distribution, versionsByMajor := range metadata.Versions {
		for majorVersion := range versionsByMajor {
			matrix.Combinations = append(matrix.Combinations, buildCombo{
				Distribution: distribution,
				MajorVersion: majorVersion,
			})
		}
	}

	// Sort for deterministic ordering, since map iteration order is random.
	slices.SortFunc(matrix.Combinations, func(a, b buildCombo) int {
		if c := cmp.Compare(a.Distribution, b.Distribution); c != 0 {
			return c
		}
		return cmp.Compare(a.MajorVersion, b.MajorVersion)
	})

	return &matrix
}

func parseExtensionMetadata(ctx context.Context, extensionDirectory *dagger.Directory) (*extensionMetadata, error) {
	hasMetadataFile, err := extensionDirectory.Exists(ctx, metadataFile)
	if err != nil {
		return nil, err
	}
	if !hasMetadataFile {
		return nil, fmt.Errorf("metadata.hcl file is missing")
	}

	data, err := extensionDirectory.File(metadataFile).Contents(ctx)
	if err != nil {
		return nil, err
	}

	return decodeExtensionMetadata([]byte(data))
}

// Decode separately so discovery compatibility can be tested without a session.
func decodeExtensionMetadata(data []byte) (*extensionMetadata, error) {
	type Config struct {
		Metadata extensionMetadata `hcl:"metadata"`
		Remain   hcl.Body          `hcl:",remain"`
	}

	var rootMeta Config
	err := hclsimple.Decode(metadataFile, data, nil, &rootMeta)
	if err != nil {
		return nil, err
	}

	// metadata is an object expression, and go-cty's struct conversion treats
	// object fields as required even when the HCL field is optional. Decode the
	// object once as a cty.Value to preserve the historical omitted=Debian
	// default without making every existing metadata.hcl grow a new field.
	type rawConfig struct {
		Metadata cty.Value `hcl:"metadata"`
		Remain   hcl.Body  `hcl:",remain"`
	}
	var raw rawConfig
	if err := hclsimple.Decode(metadataFile, data, nil, &raw); err != nil {
		return nil, err
	}
	if raw.Metadata.IsKnown() && !raw.Metadata.IsNull() && raw.Metadata.Type().IsObjectType() && raw.Metadata.Type().HasAttribute("build_system") {
		buildSystem := raw.Metadata.GetAttr("build_system")
		if !buildSystem.IsKnown() || buildSystem.IsNull() || buildSystem.Type() != cty.String || buildSystem.AsString() == "" {
			return nil, fmt.Errorf("build_system must be a nonempty string")
		}
		rootMeta.Metadata.BuildSystem = buildSystem.AsString()
	}

	if _, err := effectiveBuildSystem(&rootMeta.Metadata); err != nil {
		return nil, err
	}
	return &rootMeta.Metadata, nil
}
