package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"slices"
	"strings"
	"testing"
)

type mixedTargetFixture struct {
	Targets []struct {
		Name        string `json:"name"`
		BuildSystem string `json:"build_system"`
	} `json:"targets"`
	DebianTargets []string `json:"debian_targets"`
	PgrxTargets   []string `json:"pgrx_targets"`
}

func TestEffectiveBuildSystem(t *testing.T) {
	tests := []struct {
		name       string
		metadata   extensionMetadata
		wantSystem string
		wantErr    bool
	}{
		{name: "omitted means Debian", metadata: extensionMetadata{Name: "legacy"}, wantSystem: debianBuildSystem},
		{name: "explicit Debian", metadata: extensionMetadata{Name: "debian", BuildSystem: debianBuildSystem}, wantSystem: debianBuildSystem},
		{name: "pgrx", metadata: extensionMetadata{Name: "pg-jsonschema", BuildSystem: pgrxBuildSystem}, wantSystem: pgrxBuildSystem},
		{name: "unknown", metadata: extensionMetadata{Name: "bad", BuildSystem: "unknown"}, wantErr: true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := effectiveBuildSystem(&tt.metadata)
			if tt.wantErr {
				if err == nil {
					t.Fatal("expected an error")
				}
				return
			}
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tt.wantSystem {
				t.Fatalf("build system: got %q, want %q", got, tt.wantSystem)
			}
		})
	}
}

func TestMixedTargetRoutingFixture(t *testing.T) {
	data, err := os.ReadFile("testdata/mixed-target-routing.json")
	if err != nil {
		t.Fatalf("read mixed-target fixture: %v", err)
	}

	var fixture mixedTargetFixture
	if err := json.Unmarshal(data, &fixture); err != nil {
		t.Fatalf("decode mixed-target fixture: %v", err)
	}

	debianTargets := make([]string, 0, len(fixture.Targets))
	pgrxTargets := make([]string, 0, len(fixture.Targets))
	for _, target := range fixture.Targets {
		buildSystem, err := effectiveBuildSystem(&extensionMetadata{
			Name:        target.Name,
			BuildSystem: target.BuildSystem,
		})
		if err != nil {
			t.Fatalf("classify %q: %v", target.Name, err)
		}
		switch buildSystem {
		case debianBuildSystem:
			debianTargets = append(debianTargets, target.Name)
		case pgrxBuildSystem:
			pgrxTargets = append(pgrxTargets, target.Name)
		}
	}

	if !slices.Equal(debianTargets, fixture.DebianTargets) {
		t.Fatalf("Debian targets: got %v, want %v", debianTargets, fixture.DebianTargets)
	}
	if !slices.Equal(pgrxTargets, fixture.PgrxTargets) {
		t.Fatalf("pgrx targets: got %v, want %v", pgrxTargets, fixture.PgrxTargets)
	}
}

func TestPgrxCatalogVersionPreservesSourceTag(t *testing.T) {
	metadata := &extensionMetadata{Name: "pg-durable", BuildSystem: pgrxBuildSystem, ImageName: "pg-durable", Versions: versionMap{"trixie": {"18": {Package: "v0.2.7"}}}}
	got, err := getExtensionImage(metadata, "trixie", 18)
	if err != nil {
		t.Fatal(err)
	}
	if got != "ghcr.io/cloudnative-pg/pg-durable:v0.2.7-18-trixie" {
		t.Fatal(got)
	}
}

func TestPgrxRealMetadataInventory(t *testing.T) {
	paths, err := filepath.Glob("../../*/metadata.hcl")
	if err != nil {
		t.Fatal(err)
	}
	var pgrx []string
	for _, path := range paths {
		data, err := os.ReadFile(path)
		if err != nil {
			t.Fatal(err)
		}
		metadata, err := decodeExtensionMetadata(data)
		if err != nil {
			t.Fatalf("%s: %v", path, err)
		}
		system, err := effectiveBuildSystem(metadata)
		if err != nil {
			t.Fatal(err)
		}
		if system == pgrxBuildSystem {
			pgrx = append(pgrx, metadata.Name)
			if len(buildMatrixFromMetadata(metadata).Combinations) != 2 {
				t.Fatal(metadata.Name)
			}
		}
	}
	slices.Sort(pgrx)
	if !slices.Equal(pgrx, []string{"pg-durable", "pg-graphql", "pg-jsonschema", "pg-parquet", "pg-search", "pg-session-jwt"}) {
		t.Fatal(pgrx)
	}
}

func TestPgrxMetadataRejectsExplicitInvalidBuildSystems(t *testing.T) {
	data, err := os.ReadFile("../../pg-durable/metadata.hcl")
	if err != nil {
		t.Fatal(err)
	}
	for _, invalid := range []string{`"unknown"`, `""`, `42`, `null`} {
		content := strings.Replace(string(data), `"pgrx"`, invalid, 1)
		if _, err := decodeExtensionMetadata([]byte(content)); err == nil {
			t.Fatalf("accepted %s", invalid)
		}
	}
}

func TestPgrxCatalogDependencyAndBaseAssertions(t *testing.T) {
	if catalogDependencySQLName("pgvector") != "vector" || catalogDependencySQLName("h3") != "h3" {
		t.Fatal("SQL alias mismatch")
	}
	name, base, err := parseRequiredDependency("base-image:plpython3u")
	if err != nil || !base || name != "plpython3u" {
		t.Fatal(name, base, err)
	}
	if _, present := generateDatabaseAssertStatus(nil)["observedGeneration"]; present {
		t.Fatal("base relaxation regressed")
	}
}
