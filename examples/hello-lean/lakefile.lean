import Lake
open Lake DSL

package hello_lean {
  -- add package configuration options here
}

lean_lib HelloLean {
  -- add library configuration options here
}

@[default_target]
lean_exe hello {
  root := `Main
}
