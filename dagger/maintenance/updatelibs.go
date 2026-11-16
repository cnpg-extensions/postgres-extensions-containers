package main

import (
	"context"
	"fmt"
	"path"
	"regexp"
	"strings"

	"dagger/maintenance/internal/dagger"
)

// libsRegex matches library dependencies from apt-get output
// Format: 'url' library-name size [MD5Sum:checksum]
var libsRegex = regexp.MustCompile(`(?m)^\S+\s+(lib\S+\.deb)\s+\d+\s*(MD5Sum:\S+)?\s*$`)

func updateOSLibsOnTarget(
	ctx context.Context,
	target string,
	distribution string,
	majorVersion string,
) (*dagger.File, error) {
	postgresBaseImage := fmt.Sprintf("ghcr.io/cloudnative-pg/postgresql:%s-minimal-%s", majorVersion, distribution)
	packageName := fmt.Sprintf("postgresql-%s-%s", majorVersion, target)

	out, err := dag.Container().
		From(postgresBaseImage).
		WithUser("root").
		WithExec([]string{"apt-get", "update"}).
		WithExec([]string{"bash",
			"-c",
			"apt-get install -qq --print-uris --no-install-recommends " + packageName,
		}).Stdout(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch OS libs for extension %s (PostgreSQL %s on %s): %w",
			target, majorVersion, distribution, err)
	}

	matches := libsRegex.FindAllStringSubmatch(out, -1)
	if len(matches) == 0 {
		return nil, fmt.Errorf("no library dependencies found for extension %s (PostgreSQL %s on %s): apt-get may have failed or package has no lib dependencies",
			target, majorVersion, distribution)
	}

	var result string
	for _, m := range matches {
		line := strings.Join(m[1:], " ")
		result += strings.TrimSpace(line) + "\n"
	}

	if result == "" {
		return nil, fmt.Errorf("parsed empty content for extension %s (PostgreSQL %s on %s): regex matched but extracted no data",
			target, majorVersion, distribution)
	}

	fileName := fmt.Sprintf("%s-%s-os-libs.txt", majorVersion, distribution)
	file := dag.File(fileName, result)

	return file, nil
}

type extensionsOptions struct {
	filterOSLibs bool
	buildSystem  string
}

// ExtensionsOption is a functional option for configuring extension retrieval
type ExtensionsOption func(*extensionsOptions)

// WithOSLibsFilter returns only extensions that have AutoUpdateOsLibs set to true
func WithOSLibsFilter() ExtensionsOption {
	return func(opts *extensionsOptions) {
		opts.filterOSLibs = true
	}
}

// getExtensions retrieves a map of extensions from the source directory.
// By default, all extensions are returned, but filters can be applied.
func getExtensions(
	ctx context.Context,
	source *dagger.Directory,
	opts ...ExtensionsOption,
) (map[string]string, error) {
	options := &extensionsOptions{}
	for _, opt := range opts {
		opt(options)
	}

	inventory, err := recipeInventory(ctx, source)
	if err != nil {
		return nil, err
	}
	extensions := make(map[string]string)
	for name, metadata := range inventory {
		if options.buildSystem != "" && metadata.BuildSystem != options.buildSystem {
			continue
		}
		if options.filterOSLibs && (metadata.BuildSystem != debianBuildSystem || !metadata.AutoUpdateOsLibs) {
			continue
		}
		extensions[metadata.RecipePath] = name
	}
	return extensions, nil
}

// recipeFamily accepts only the three explicit recipe depths.
func recipeFamily(p string) string {
	parts := strings.Split(p, "/")
	if len(parts) == 2 && parts[1] == metadataFile && parts[0] != "source-build" && parts[0] != "pgrx" && parts[0] != "universe" {
		return debianBuildSystem
	}
	if len(parts) == 3 && parts[2] == metadataFile {
		switch parts[0] {
		case "pgrx", "universe":
			return parts[0]
		}
	}
	return ""
}

func recipeInventory(ctx context.Context, source *dagger.Directory) (map[string]*extensionMetadata, error) {
	var paths []string
	for _, pattern := range []string{"*/metadata.hcl", "pgrx/*/metadata.hcl", "universe/*/metadata.hcl"} {
		matches, err := source.Glob(ctx, pattern)
		if err != nil {
			return nil, err
		}
		paths = append(paths, matches...)
	}
	return loadRecipeInventory(paths, func(p string) (*extensionMetadata, error) {
		return parseExtensionMetadata(ctx, source.Directory(path.Dir(p)))
	})
}

func loadRecipeInventory(paths []string, load func(string) (*extensionMetadata, error)) (map[string]*extensionMetadata, error) {
	inventory := map[string]*extensionMetadata{}
	for _, p := range paths {
		family := recipeFamily(p)
		if family == "" {
			continue
		}
		metadata, err := load(p)
		if err != nil {
			return nil, fmt.Errorf("%s: %w", p, err)
		}
		metadata.BuildSystem, metadata.RecipePath = family, path.Dir(p)
		if previous, ok := inventory[metadata.Name]; ok {
			return nil, fmt.Errorf("duplicate logical name %q in %s and %s", metadata.Name, previous.RecipePath, metadata.RecipePath)
		}
		inventory[metadata.Name] = metadata
	}
	return inventory, nil
}

func lookupExtensionMetadata(ctx context.Context, source *dagger.Directory, name string) (*extensionMetadata, error) {
	inventory, err := recipeInventory(ctx, source)
	if err != nil {
		return nil, err
	}
	metadata, ok := inventory[name]
	if !ok {
		return nil, fmt.Errorf("unknown extension %q", name)
	}
	return metadata, nil
}

func extensionsDirectories(ctx context.Context, source *dagger.Directory) ([]*dagger.Directory, error) {
	inventory, err := recipeInventory(ctx, source)
	if err != nil {
		return nil, err
	}
	var directories []*dagger.Directory
	for _, metadata := range inventory {
		directories = append(directories, source.Directory(metadata.RecipePath))
	}
	return directories, nil
}
