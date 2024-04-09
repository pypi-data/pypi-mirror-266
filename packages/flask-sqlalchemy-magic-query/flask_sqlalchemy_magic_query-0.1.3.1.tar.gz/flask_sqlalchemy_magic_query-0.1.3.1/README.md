## Description

A simple decorator to speed up development using flask_sqlalchemy, place the decorator pass the model and done! it works!

## Usage/Examples

Place the `@filter_query` passing the model as argument and enjoy!

### Usage example on users endpoint with Users model:
```python
@users.route('/users', methods=["GET"])
@filter_query(Users)
def get_users(*args, **kwargs):
    return make_response(jsonify(kwargs.get('data')), total=kwargs.get('total')), 200)
```

### then you can make a http request passing arguments:
```
curl --location 'http://127.0.0.1:5000/users?email__like__=%gabriel%&id__eq__=2
```

response example:
```
{
    "data": [
        {
            "email": "gabriel.ligoski@gmail.com",
            "id": 2,
            "username": "ligoski"
        }
    ],
    "total": 1
}
```

### currently supported filters:
- gte
    * Example: ```curl --location 'http://127.0.0.1:5000/users?id__gte__=2```
- gt
    * Example: ```curl --location 'http://127.0.0.1:5000/users?id__gt__=2```
- lte
    * Example: ```curl --location 'http://127.0.0.1:5000/users?id__lte__=2```
- lt
    * Example: ```curl --location 'http://127.0.0.1:5000/users?id__lt__=2```
- like
    * Example: ```curl --location 'http://127.0.0.1:5000/users?email__like__=%gabriel%```
- in
    * Example: ```curl --location 'http://127.0.0.1:5000/users?email__in__=gabriel.ligoski@gmail.com,admin@gmail.com,teste@hotmail.com```
- eq
    * Example: ```curl --location 'http://127.0.0.1:5000/users?id__eq__=2```
