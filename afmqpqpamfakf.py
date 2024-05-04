from dadata import Dadata


token = "1c43107faa2f7ad485f777c924c9c0d38459e62e"
secret = "e23b47eb7e0ce34d86bd81d46ebd780f2cf0a02f"
dadata = Dadata(token, secret)
result = dadata.clean("address", "Орск")
print(result)