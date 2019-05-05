from voluptuous import Required, Schema


user_schema = Schema({
    Required('username'): str,
    Required('password'): str,
    Required('superuser'): bool,
    Required('full_name'): str,
    Required('email'): str
})

use_case_schema = Schema({
    Required('id'): int
}, extra=True)

add_batch_schema = Schema({
    Required('batch_name'): str,
    Required('create_by'): int
}, extra=True)
