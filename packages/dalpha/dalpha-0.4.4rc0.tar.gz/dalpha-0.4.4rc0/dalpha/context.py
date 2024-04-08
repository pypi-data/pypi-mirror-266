from dataclasses import dataclass

@dataclass
class Context:
    inference_id: int = None
    service_code: str = None
    env: str = None
    evaluate_id: int = None
    account_id: int = None

context = Context()
    
def set_context(ctx):
    global context
    context = ctx

def set_context_evaluate(evaluate_id, account_id):
    global context
    context.evaluate_id = evaluate_id
    context.account_id = account_id

def clear_context_evaluate():
    global context
    context.evaluate_id = None
    context.account_id = None

def get_context():
    return context