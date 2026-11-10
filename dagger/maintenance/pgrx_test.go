package main

import (
	"os"
	"testing"
)

func TestDecodePgrxBuildSystem(t *testing.T) {
	data, err := os.ReadFile("../../pg-durable/metadata.hcl")
	if err != nil {
		t.Fatal(err)
	}
	metadata, err := decodeExtensionMetadata(data)
	if err != nil {
		t.Fatal(err)
	}
	// Losing the downstream decoder hook must not silently classify PGRX as Debian.
	if metadata.BuildSystem != pgrxBuildSystem {
		t.Fatalf("decoded build system = %q, want %q", metadata.BuildSystem, pgrxBuildSystem)
	}
}

func TestEffectiveBuildSystem(t *testing.T) {
	tests := []struct {
		name       string
		metadata   extensionMetadata
		wantSystem string
	}{
		{name: "omitted means Debian", metadata: extensionMetadata{Name: "legacy"}, wantSystem: debianBuildSystem},
		{name: "explicit Debian", metadata: extensionMetadata{Name: "debian", BuildSystem: debianBuildSystem}, wantSystem: debianBuildSystem},
		{name: "pgrx", metadata: extensionMetadata{Name: "pg-jsonschema", BuildSystem: pgrxBuildSystem}, wantSystem: pgrxBuildSystem},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := effectiveBuildSystem(&tt.metadata)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tt.wantSystem {
				t.Fatalf("build system: got %q, want %q", got, tt.wantSystem)
			}
		})
	}
}

func TestPgrxCatalogVersionPreservesSourceTag(t *testing.T) {
	metadata := &extensionMetadata{Name: "pg-durable", BuildSystem: pgrxBuildSystem, ImageName: "pg-durable", Versions: versionMap{"trixie": {"18": {Package: "v0.2.7"}}}}
	got, err := getExtensionImage(metadata, "trixie", 18)
	if err != nil {
		t.Fatal(err)
	}
	if got != "ghcr.io/cnpg-extensions/pg-durable:v0.2.7-18-trixie" {
		t.Fatal(got)
	}
}

func TestPgrxCatalogDependencySQLName(t *testing.T) {
	if catalogDependencySQLName("pgvector") != "vector" || catalogDependencySQLName("h3") != "h3" {
		t.Fatal("SQL alias mismatch")
	}
}
