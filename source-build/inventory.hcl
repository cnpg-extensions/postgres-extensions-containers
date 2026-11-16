// Let Bake's HCL evaluator parse metadata rather than maintaining another parser.
target "inventory" {
  args = { METADATA = jsonencode(metadata) }
}
