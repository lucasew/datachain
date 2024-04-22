stdlib = {}

def evaluator_item(name=None, eval_args=True, register=True):
    def ret(func):
        func_name = name if name is not None else func.__name__
        final_func = func
        if eval_args:
            def final_func(env, *args, **kwargs):
                return func(env, *list(map(lambda item: _eval(env, item), args)), **_eval(env, kwargs))
        final_func.__name__ = func_name
        if register:
            stdlib[func_name] = final_func
        return final_func
    return ret

@evaluator_item(name='eval', eval_args=False)
def _eval(env, expr):
    if expr is None:
        return None
    if isinstance(expr, dict):
        if expr.get('_eval'):
            return {k: _eval(v) for k, v in expr.items()}
        return expr
    if isinstance(expr, list) and len(expr) > 0 and isinstance(expr[0], str):
        kwargs = {}
        args = []
        for arg in expr[1:]:
            if isinstance(arg, dict):
                kwargs = {**kwargs, **arg}
            else:
                args.append(arg)
        fn = env[expr[0]]
        return fn(env, *args, **kwargs)
    return expr

@evaluator_item()
def answer_to_life_universe_and_everything(env):
    return 42

def lfold(pair_fn):
    def ret(env, *values):
        assert len(values) > 0
        accum = values[0]
        for item in values[1:]:
            accum = pair_fn(env, accum, item)
        return accum
    return ret

evaluator_item(name="+")(lfold(lambda env, x, y: x + y))
evaluator_item(name="-")(lfold(lambda env, x, y: x - y))
evaluator_item(name="*")(lfold(lambda env, x, y: x * y))
evaluator_item(name="/")(lfold(lambda env, x, y: x / y))
evaluator_item(name="//")(lfold(lambda env, x, y: x // y))

@evaluator_item()
def truep(env, arg):
    if arg is None:
        return False
    if arg is False:
        return False
    return True

@evaluator_item()
def stringp(env, arg):
    if isinstance(arg, str):
        return arg
    return None

@evaluator_item()
def intp(env, arg):
    print('intp chamado', arg)
    if isinstance(arg, int):
        return arg
    return None

@evaluator_item(name='and', eval_args=False)
def _and(env, *args):
    for item in args:
        item = _eval(env, item)
        if not truep(env, item):
            return False
    return args[-1]

@evaluator_item(name='or')
def _or(env, *args):
    for item in args:
        item = _eval(env, item)
        if truep(env, item):
            return item
    return None

@evaluator_item(name='if', eval_args=False)
def _if(env, cond, if_true, if_false=None):
    if truep(env, _eval(env, cond)):
        return _eval(env, if_true)
    else:
        return _eval(env, if_false)

@evaluator_item(name='var', eval_args=False)
def _var(env, var):
    assert type(var) == str
    return env.get(var)

@evaluator_item(name='let_recursive', eval_args=False)
def _let_recursive(env, stmts, expr):
    new_env = {**env}
    assert len(stmts) % 2 == 0
    for i in range(0, len(stmts), 2):
        k = stmts[i]
        v = stmts[i + 1]
        new_env[k] = _eval(new_env, v)
    return _eval(new_env, expr)

@evaluator_item(name='wrap_native')
def wrap_native_callable(env, callable, eval_args=True):
    def wrapped_function(env, *args, **kwargs):
        return callable(*args, **kwargs)
    return evaluator_item(register=False, eval_args=eval_args)(wrapped_function)

class Evaluator():
    def __init__(self, env):
        self.env = {**stdlib, **env}

    def eval(self, expr):
        return self.env['eval'](self.env, expr)
