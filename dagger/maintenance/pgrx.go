package main

import (
	"fmt"
	"strconv"

	"github.com/hashicorp/hcl/v2"
	"github.com/hashicorp/hcl/v2/hclsimple"
	"github.com/zclconf/go-cty/cty"
)

// pgvector is the catalog identifier; vector is its SQL extension name.
func catalogDependencySQLName(name string) string {
	if name == "pgvector" {
		return "vector"
	}
	return name
}

// PGRX releases use source tags verbatim; Debian retains its epoch/version rules.
func extensionImageVersion(metadata *extensionMetadata, distribution string, major int) (string, error) {
	system, err := effectiveBuildSystem(metadata)
	if err != nil {
		return "", err
	}
	if system == pgrxBuildSystem {
		version, ok := metadata.Versions[distribution][strconv.Itoa(major)]
		if !ok || version.Package == "" {
			return "", fmt.Errorf("missing PGRX version for %s/%d", distribution, major)
		}
		return version.Package, nil
	}
	return extractExtensionVersion(metadata.Versions, distribution, major)
}

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

// decodeBuildSystem reads the optional downstream field after upstream typed decoding.
func decodeBuildSystem(data []byte, metadata *extensionMetadata) error {
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
		return err
	}
	if raw.Metadata.IsKnown() && !raw.Metadata.IsNull() && raw.Metadata.Type().IsObjectType() && raw.Metadata.Type().HasAttribute("build_system") {
		buildSystem := raw.Metadata.GetAttr("build_system")
		if !buildSystem.IsKnown() || buildSystem.IsNull() || buildSystem.Type() != cty.String || buildSystem.AsString() == "" {
			return fmt.Errorf("build_system must be a nonempty string")
		}
		metadata.BuildSystem = buildSystem.AsString()
	}

	if _, err := effectiveBuildSystem(metadata); err != nil {
		return err
	}
	return nil
}

// WithBuildSystemFilter restricts discovery to one build-system family. An
// omitted build_system in metadata is treated as Debian for compatibility.
func WithBuildSystemFilter(buildSystem string) ExtensionsOption {
	return func(opts *extensionsOptions) {
		opts.buildSystem = buildSystem
	}
}

// normalizeBuildSystemFilter keeps Debian as the default for existing callers.
func normalizeBuildSystemFilter(buildSystem string) (string, error) {
	switch buildSystem {
	case "":
		buildSystem = debianBuildSystem
	case "all":
		buildSystem = ""
	case debianBuildSystem, pgrxBuildSystem:
	default:
		return "", fmt.Errorf("unsupported build system: %q", buildSystem)
	}
	return buildSystem, nil
}
