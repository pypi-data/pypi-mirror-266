from pymongo.errors import OperationFailure, ConnectionFailure
# TODO: redis, postgres
# TODO: print -> click.echo ?

def exception_handler(func):
    def inner_function(*args, **kwargs):
        err_count = 0
        err_limit = 3
        while True and err_count < err_limit:
            try:
                err_count += 1
                return func(*args, **kwargs)
            except (ConnectionFailure,) as e:
                print(f"MongoDB connection error: {e}")
                print(f"retrying {err_count}/{err_limit} ...")
                # args[0]._reset_connection()
            except OperationFailure as e:
                print(f"MongoDB OperationFailure: {e}")
                raise e
        else:
            print(f"MongoDB exception for customer")
            # TODO: HTTP EXCEPTION FOR CUSTOMER, but keep thread alive

    return inner_function