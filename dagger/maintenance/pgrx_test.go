package main

import (
	"os"
	"testing"
)

func TestDecodePgrxBuildSystem(t *testing.T) {
	data, err := os.ReadFile("../../pgrx/pg-durable/metadata.hcl")
	if err != nil {
		t.Fatal(err)
	}
	metadata, err := decodeExtensionMetadata(data)
	if err != nil {
		t.Fatal(err)
	}
	// The upstream decoder accepts retained legacy metadata without reading it.
	if metadata.BuildSystem != "" {
		t.Fatalf("decoded legacy build system = %q, want empty", metadata.BuildSystem)
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
	metadata := &extensionMetadata{Name: "pg-durable", BuildSystem: pgrxBuildSystem, ImageName: "pg-durable", Versions: versionMap{"trixie": {"18": {Package: "v0.2.7-rc.1-extra"}}}}
	got, err := getExtensionImage(metadata, "trixie", 18)
	if err != nil {
		t.Fatal(err)
	}
	if got != "ghcr.io/cnpg-extensions/pg-durable:0.2.7-rc.1-extra-18-trixie" {
		t.Fatal(got)
	}
}

func TestPgrxCatalogDependencySQLName(t *testing.T) {
	if catalogDependencySQLName("pgvector") != "vector" || catalogDependencySQLName("h3") != "h3" {
		t.Fatal("SQL alias mismatch")
	}
}
