package main

import (
	"fmt"
	"strconv"
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
