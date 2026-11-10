package main

import (
	"errors"
	"testing"
)

func TestCatalogDependencyUsesCatalogImage(t *testing.T) {
	info, err := catalogTestingDependency("pgvector")
	if err != nil {
		t.Fatal(err)
	}
	if info.Configuration.Name != "pgvector" || info.Configuration.ImageVolumeSource.Reference != "" || info.SQLName != "vector" || info.Version != "" || !info.CreateExtension {
		t.Fatalf("unexpected catalog dependency: %+v, configuration: %+v", info, info.Configuration)
	}
	for _, name := range []string{"", "catalog:pgvector", "../pgvector", "pg vector"} {
		if _, err := catalogTestingDependency(name); err == nil {
			t.Errorf("accepted invalid name %q", name)
		}
	}
}

func TestDependencyPrefixesRemainDistinct(t *testing.T) {
	for _, tc := range []struct {
		input, name string
		base        bool
	}{
		{"base-image:btree_gist", "btree_gist", true},
		{"postgis", "postgis", false},
	} {
		name, base, err := parseRequiredDependency(tc.input)
		if err != nil || name != tc.name || base != tc.base {
			t.Fatalf("%q: %q, %v, %v", tc.input, name, base, err)
		}
	}
	if _, _, err := parseRequiredDependency("base-image:"); err == nil {
		t.Fatal("accepted empty base-image dependency")
	}
}

func TestNormalizeBuildSystemFilter(t *testing.T) {
	for input, want := range map[string]string{"": "debian", "debian": "debian", "pgrx": "pgrx", "all": ""} {
		got, err := normalizeBuildSystemFilter(input)
		if err != nil || got != want {
			t.Fatalf("%q: got %q, %v; want %q", input, got, err, want)
		}
	}
	if _, err := normalizeBuildSystemFilter("typo"); err == nil {
		t.Fatal("accepted unknown build system")
	}
}

func TestResolveDependenciesThroughCatalog(t *testing.T) {
	infos, err := resolveDependencies([]string{"base-image:btree_gist", "pgvector", "local"},
		func(name string) (*extensionMetadata, error) {
			switch name {
			case "pgvector":
				return nil, nil
			case "local":
				return &extensionMetadata{Name: "local-catalog-name", SQLName: "local_sql", CreateExtension: false, ImageName: "must-not-be-used"}, nil
			default:
				t.Fatalf("unexpected metadata lookup %q", name)
				return nil, nil
			}
		})
	if err != nil {
		t.Fatal(err)
	}
	if len(infos) != 3 {
		t.Fatalf("got %d dependencies", len(infos))
	}
	if infos[0].Configuration != nil || infos[0].SQLName != "btree_gist" || !infos[0].CreateExtension {
		t.Fatalf("unexpected base-image dependency: %+v", infos[0])
	}
	for _, info := range infos[1:] {
		if info.Configuration.ImageVolumeSource.Reference != "" || info.Version != "" {
			t.Fatalf("dependency overrides catalog image/version: %+v", info)
		}
	}
	if infos[1].Configuration.Name != "pgvector" || infos[1].SQLName != "vector" || !infos[1].CreateExtension {
		t.Fatalf("unexpected external dependency: %+v", infos[1])
	}
	if infos[2].Configuration.Name != "local-catalog-name" || infos[2].SQLName != "local_sql" || infos[2].CreateExtension {
		t.Fatalf("local SQL metadata lost: %+v", infos[2])
	}
}

func TestResolveDependenciesPropagatesMetadataError(t *testing.T) {
	want := errors.New("invalid local metadata")
	_, err := resolveDependencies([]string{"local"}, func(string) (*extensionMetadata, error) { return nil, want })
	if !errors.Is(err, want) {
		t.Fatalf("got %v, want metadata error", err)
	}
}
