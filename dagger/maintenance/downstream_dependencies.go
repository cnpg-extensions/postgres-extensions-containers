package main

import (
	"context"
	"fmt"
	"strings"

	"dagger/maintenance/internal/dagger"
)

const baseImageDependencyPrefix = "base-image:"

// resolveTestingDependencies uses the cluster catalog for every bare dependency
// name. Local metadata supplies SQL settings only, never image coordinates.
// Missing catalog entries fail cluster reconciliation/E2E.
func resolveTestingDependencies(ctx context.Context, source *dagger.Directory,
	dependencies []string,
) ([]*testingExtensionInfo, error) {
	return resolveDependencies(dependencies, func(name string) (*extensionMetadata, error) {
		exists, err := source.Exists(ctx, name)
		if err != nil {
			return nil, err
		}
		if !exists {
			return nil, nil
		}
		metadata, err := parseExtensionMetadata(ctx, source.Directory(name))
		if err != nil {
			return nil, fmt.Errorf("failed to parse dependency metadata %q: %w", name, err)
		}
		return metadata, nil
	})
}

func resolveDependencies(dependencies []string,
	lookupMetadata func(string) (*extensionMetadata, error),
) ([]*testingExtensionInfo, error) {
	var out []*testingExtensionInfo
	for _, requiredDependency := range dependencies {
		dep, isBaseImageDependency, err := parseRequiredDependency(requiredDependency)
		if err != nil {
			return nil, err
		}
		if isBaseImageDependency {
			out = append(out, &testingExtensionInfo{
				SQLName:         dep,
				CreateExtension: true,
			})
			continue
		}

		info, err := catalogTestingDependency(dep)
		if err != nil {
			return nil, err
		}
		metadata, err := lookupMetadata(dep)
		if err != nil {
			return nil, err
		}
		if metadata != nil {
			info.Configuration.Name = metadata.Name
			info.SQLName = metadata.SQLName
			info.CreateExtension = metadata.CreateExtension
		}
		out = append(out, info)
	}

	return out, nil
}

func parseRequiredDependency(dependency string) (string, bool, error) {
	if !strings.HasPrefix(dependency, baseImageDependencyPrefix) {
		return dependency, false, nil
	}

	name := strings.TrimPrefix(dependency, baseImageDependencyPrefix)
	if name == "" {
		return "", false, fmt.Errorf("base-image dependency %q has no extension name", dependency)
	}

	return name, true, nil
}

// catalogTestingDependency deliberately supplies no image override or version:
// CNPG resolves the named extension using the selected catalog.
func catalogTestingDependency(name string) (*testingExtensionInfo, error) {
	if name == "" || strings.ContainsAny(name, ":/ \t\r\n") {
		return nil, fmt.Errorf("invalid catalog dependency name %q", name)
	}
	return &testingExtensionInfo{
		Configuration:   &ExtensionConfiguration{Name: name},
		SQLName:         catalogDependencySQLName(name),
		CreateExtension: true,
	}, nil
}
