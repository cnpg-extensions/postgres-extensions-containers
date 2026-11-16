package main

import (
	"fmt"
	"strconv"
	"strings"
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
	if system != debianBuildSystem {
		version, ok := metadata.Versions[distribution][strconv.Itoa(major)]
		if !ok || version.Package == "" {
			return "", fmt.Errorf("missing source version for %s/%d", distribution, major)
		}
		return strings.TrimPrefix(version.Package, "v"), nil
	}
	return extractExtensionVersion(metadata.Versions, distribution, major)
}

const (
	debianBuildSystem   = "debian"
	pgrxBuildSystem     = "pgrx"
	universeBuildSystem = "universe"
)

// effectiveBuildSystem preserves the repository's historical default while
// rejecting unknown explicit values at the target-list boundary.
func effectiveBuildSystem(metadata *extensionMetadata) (string, error) {
	if metadata.BuildSystem == "" {
		return debianBuildSystem, nil
	}
	if metadata.BuildSystem != debianBuildSystem && metadata.BuildSystem != pgrxBuildSystem && metadata.BuildSystem != universeBuildSystem {
		return "", fmt.Errorf("unsupported build_system %q for target %q", metadata.BuildSystem, metadata.Name)
	}
	return metadata.BuildSystem, nil
}

// WithBuildSystemFilter restricts discovery to one location-derived family.
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
	case debianBuildSystem, pgrxBuildSystem, universeBuildSystem:
	default:
		return "", fmt.Errorf("unsupported build system: %q", buildSystem)
	}
	return buildSystem, nil
}
