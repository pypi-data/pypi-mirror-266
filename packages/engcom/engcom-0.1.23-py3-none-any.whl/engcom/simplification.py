"""Simplification functions for SymPy"""

import sympy as sp
from IPython.display import display, Math, Latex, display_latex

def apply_to_numden(expr, fun, numer=True, denom=True):
	"""Apply a function to the numerator, denominator, 
	or both of a SymPy expression
	"""
	num, den = sp.fraction(expr.cancel())
	if numer:
		num = fun(num)
	if denom:
		den = fun(den)
	return num/den

def display_dict(d):
	"""Display a dictionary with pretty-printing"""
	for k, v in d.items():
		display(sp.Eq(k, v))

def _trig_two_to_one_sin_rule(a, b, u):
	"""Replacement rule for sin(u) in a cos(u) + b sin(u) for 
	converting to a single sin term with a phase
	
	The identity applied is:
		a cos u + b sin u = sqrt(a^2 + b^2) sin(u + atan(a/b))
	Returns: A dictionary for replacing sin(u)
	"""
	identity = a*sp.cos(u) + b*sp.sin(u) + \
		- sp.sqrt(a**2 + b**2)*sp.sin(u + sp.atan(a/b))
	sol = sp.solve(identity, [sp.sin(u)], dict=True)
	return sol[0]

def _trig_two_to_one_cos_rule(a, b, u):
	"""Replacement rule for sin(u) in a cos(u) + b sin(u) for 
	converting to a single cos term with a phase
	
	The identity applied is:
		a cos u + b sin u = sqrt(a^2 + b^2) cos(u - atan(b/a))
	Returns: A dictionary for replacing sin(u)
	"""
	identity = a*sp.cos(u) + b*sp.sin(u) + \
		- sp.sqrt(a**2 + b**2)*sp.cos(u - sp.atan(b/a))
	sol = sp.solve(identity, [sp.sin(u)], dict=True)
	return sol[0]

def trig_two_to_one(expr: sp.Expr, to: str = "sin"):
	"""Rewrites sin and cos terms that share arguments to single sin 
	or cos terms
	
	Applies the following identity:
		a cos u + b sin u = sqrt(a^2 + b^2) sin(u + atan(a/b))
	or
		a cos u + b sin u = sqrt(a^2 + b^2) cos(u - atan(b/a))
	depending on the ``to`` argument.
	
	Args:
		expr: The symbolic expression containing sin(u) and cos(u)
		to: Rewrite with "sin" (default) or "cos"
	"""
	expr = expr.simplify()
	# Identify sin terms
	w1 = sp.Wild("w1", exclude=[1])
	w2 = sp.Wild("w2")
	sin_terms = expr.find(w1*sp.sin(w2))
	sin_arg_amps = {}  # To be: {sin argument: sine amplitude}
	for term in sin_terms:
		arg_amp_rules = term.match(w1*sp.sin(w2))
		sin_arg_amps[arg_amp_rules[w2]] = arg_amp_rules[w1]
	# Identify cos terms
	cos_terms = expr.find(w1*sp.cos(w2))
	cos_arg_amps = {}  # To be: {sin argument: sine amplitude}
	for term in cos_terms:
		arg_amp_rules = term.match(w1*sp.cos(w2))
		cos_arg_amps[arg_amp_rules[w2]] = arg_amp_rules[w1]
	# Replace with wildcard rule
	for sin_arg, sin_amp in sin_arg_amps.items():
		if to == "sin":
			if sin_arg in cos_arg_amps.keys():
				cos_amp = cos_arg_amps[sin_arg]
				sin_rule = _trig_two_to_one_sin_rule(
					cos_amp, sin_amp, sin_arg
				)
				expr = expr.subs(sin_rule)
		elif to == "cos":
			if sin_arg in cos_arg_amps.keys():
				cos_amp = cos_arg_amps[sin_arg]
				cos_rule = _trig_two_to_one_cos_rule(
					cos_amp, sin_amp, sin_arg
				)
				expr = expr.subs(cos_rule)
	return expr.simplify()