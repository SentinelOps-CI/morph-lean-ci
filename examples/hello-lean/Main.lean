import Lean

/-- A simple function that adds two natural numbers -/
def add_nat (a b : Nat) : Nat := a + b

/-- Lemma: Adding zero to a number gives the same number -/
theorem add_zero (n : Nat) : add_nat n 0 = n := by
  rw [add_nat]
  exact Nat.add_zero n

/-- Lemma: Addition is commutative -/
theorem add_comm (a b : Nat) : add_nat a b = add_nat b a := by
  rw [add_nat, add_nat]
  exact Nat.add_comm a b

/-- Lemma: Addition is associative -/
theorem add_assoc (a b c : Nat) : add_nat (add_nat a b) c = add_nat a (add_nat b c) := by
  rw [add_nat, add_nat, add_nat]
  exact Nat.add_assoc a b c

/-- Main function that demonstrates the lemmas -/
def main : IO Unit := do
  IO.println "Hello, Lean!"
  IO.println s!"add_nat 5 3 = {add_nat 5 3}"
  IO.println s!"add_zero 7 = {add_zero 7}"
  IO.println s!"add_comm 2 8 = {add_comm 2 8}"
  IO.println s!"add_assoc 1 2 3 = {add_assoc 1 2 3}"
  IO.println "All lemmas proved successfully! 🎉"
