package main

import (
	"testing"
)

func TestRecipeDepths(t *testing.T) {
	for path, want := range map[string]string{
		"h3/metadata.hcl": "debian", "pgrx/example/metadata.hcl": "pgrx", "universe/example/metadata.hcl": "universe",
		"source-build/metadata.hcl": "", "source-build/pgrx/example/metadata.hcl": "", "pgrx/templates/fixtures/metadata.hcl": "", "test/fixtures/metadata.hcl": "",
	} {
		if got := recipeFamily(path); got != want {
			t.Errorf("%s: %s != %s", path, got, want)
		}
	}
}

func TestLocationFamiliesPreserveSourceVersions(t *testing.T) {
	for _, family := range []string{"pgrx", "universe"} {
		m := &extensionMetadata{BuildSystem: family, Versions: versionMap{"trixie": {"18": {Package: "v1.2.3-preview.4"}}}}
		got, err := extensionImageVersion(m, "trixie", 18)
		if err != nil {
			t.Fatal(err)
		}
		if family != "debian" && got != "1.2.3-preview.4" {
			t.Fatal(got)
		}
	}
}

func TestInventoryDuplicateBeforeSelectionAndLocationContext(t *testing.T) {
	paths := []string{"debian/metadata.hcl", "pgrx/source/metadata.hcl", "universe/other/metadata.hcl", "source-build/templates/metadata.hcl"}
	inventory, err := loadRecipeInventory(paths, func(p string) (*extensionMetadata, error) {
		name := "source"
		if p == paths[0] {
			name = "debian"
		}
		if p == paths[2] {
			name = "other"
		}
		return &extensionMetadata{Name: name, BuildSystem: "legacy-ignored"}, nil
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(inventory) != 3 || inventory["source"].RecipePath != "pgrx/source" || inventory["other"].BuildSystem != "universe" {
		t.Fatalf("%+v", inventory)
	}
	_, err = loadRecipeInventory(paths, func(string) (*extensionMetadata, error) { return &extensionMetadata{Name: "duplicate"}, nil })
	if err == nil {
		t.Fatal("accepted duplicate logical names")
	}
}
