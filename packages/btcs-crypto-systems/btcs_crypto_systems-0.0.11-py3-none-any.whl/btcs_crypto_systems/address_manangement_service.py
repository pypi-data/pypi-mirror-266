import requests
from dataclasses import dataclass, field
import json
import curlify


@dataclass
class AMS:
    env:str = "test"
    base_url:str = field(init=False)
    cookie_value:str = None
    log_requests:bool = False
    log_reponses:bool = False
    log_results:bool = False
    cookie_string:str = field(init=False, default=None)
    read_only:bool = field(init=False, default=True)
    
    
    def __post_init__(self):
        self.base_url = f"https://ams.btcs{self.env}.net/api/AddressManagement"
        self.cookie_string = f".AspNetCore.Cookies={self.cookie_value}; Path=/; Secure; HttpOnly;" 
        if self.cookie_value:
            self.read_only = False

    def get_addresses(self, blockchain_id=None, include_balances=None, limit=99999999999999, account_ref=None, include_balance_groups=None, is_pay=None, is_active=None, is_contract=None, is_deposit=None, ownership=None, account_asset_id=None, customer_id=None, addresses=None, tags=None):
        page = 0
        page_size = 100
        total = 0
        take_now = page_size
        addresses = []

        while True:
            try:
                # respect the limit
                if limit - (total + page_size*page) <= 0:
                    break
                elif limit - (total + page_size*page) < page_size:
                    take_now = limit - (total + page_size*page)
                url = ""
                params = AMS.remove_none_fields({
                    "Skip": page*take_now,
                    "Take": take_now,
                    "AccountRef": account_ref,
                    "BlockchainId": blockchain_id,
                    "IncludeBalances": include_balances,
                    "IncludeBalanceGroups": include_balance_groups,
                    "IsPay": is_pay,
                    "IsActive": is_active,
                    "IsContract": is_contract,
                    "IsDeposit": is_deposit,
                    "Ownership": ownership,
                    "AccountAssetId": account_asset_id,
                    "CustomerId": customer_id,
                    "Addresses": addresses,
                    "Tags": tags
                })

                r = requests.request("GET", f"{self.base_url}/addresses", params=params)
                addresses_res = r.json()
                if self.log_reponses:
                    print(f"{r.status_code}: {r.text}")
                addresses.extend(addresses_res)
                page += 1
                total += take_now

                if self.log_results:
                    print(f"collected {total} addresses...")
                if len(addresses_res) == 0:
                    break

            except:
                print("Error with URL: {}".format(url))
        
        return addresses
    
    def tag_address(self, address, blockchain_id, tag):
        if self.read_only:
            raise Exception("No cookie provided.")

        data = json.dumps({
            "addresses": [
                {
                "blockchainId": blockchain_id,
                "address": address
                }
            ],
            "tags": [
                {
                "tagName": tag
                }
            ]
        })

        headers = {
            'cookie': self.cookie_string,
            'Content-Type': 'application/json'
        }

        r = requests.patch(url=f"{self.base_url}/tag-address", data=data, headers=headers)
        
        if self.log_requests:
            print(curlify.to_curl(r.request))
        
        return r

    def attach_address(self, address:str, blockchain_id:int, account_ref:str):
        if self.read_only:
            raise Exception("No cookie provided.")
        
        data = json.dumps({
            "blockchainId": blockchain_id,
            "accountRef": account_ref,
            "addresses": [
                address
            ]
        })

        headers = {
            'cookie': self.cookie_string,
            'Content-Type': 'application/json'
        }

        r = requests.patch(url=f"{self.base_url}/attach-addresses", data=data, headers=headers)
        if self.log_requests:
            print(curlify.to_curl(r.request))
        return r
    
    def detach_address(self, address:str, blockchain_id:int, account_ref:str):
        if self.read_only:
            raise Exception("No cookie provided.")
        
        data = json.dumps({
            "blockchainId": blockchain_id,
            "accountRef": account_ref,
            "address": address
        })

        headers = {
            'cookie': self.cookie_string,
            'Content-Type': 'application/json'
        }

        r = requests.patch(url=f"{self.base_url}/detach-address", data=data, headers=headers)

        if self.log_requests:
            print(curlify.to_curl(r.request))

        return r

    def upsert_address(self, blockchain_id:int, address:str, ownership:str=None, is_active:bool=None, is_deposit:bool=None, is_contract:bool=None, vault_account_ref:str=None, location:str=None, fee_booking_mode:str=None, fee_booking_height:bool=None, is_pay:bool=None, passphrase:str=None, account_ref:str=None, tags:list[str]=None):
        if self.read_only:
            raise Exception("No cookie provided.")
        
        data_dict = AMS.remove_none_fields({
            "ownership": ownership,
            "blockchainId": blockchain_id,
            "address": address,
            "isActive": is_active,
            "isDeposit": is_deposit,
            "isContract": is_contract,
            "vaultAccountRef": vault_account_ref,
            "location": location,
            "feeBookingMode": fee_booking_mode,
            "feeBookingStartHeight": fee_booking_height,
            "isPay": is_pay,
            "passPhrase": passphrase,
            "tags": tags,
            "accountRef": account_ref
        })

        data = json.dumps(data_dict)

        headers = {
            'cookie': self.cookie_string,
            'Content-Type': 'application/json'
        }

        r = None

        if self.is_detached(address=address, blockchain_id=blockchain_id):
            print(f"{self.base_url}/address-detached")
            r = requests.patch(url=f"{self.base_url}/address-detached", data=data, headers=headers)
        else:
            account_ref = self.get_account_refs(self, address, blockchain_id)[0]
            print(f"{self.base_url}/address")
            r = requests.patch(url=f"{self.base_url}/address", data=data, headers=headers)
        
        if self.log_requests:
            print(curlify.to_curl(r.request))

        return r

    def is_detached(self, address:str, blockchain_id:int):
        r = requests.request("GET", f"{self.base_url}/addresses/{blockchain_id}/{address}")

        if self.log_reponses:
            print(f"{r.status_code}: {r.text}")

        if self.log_reponses:
            print(curlify.to_curl(r.request))
        try:
            j = r.json()
            return j["isDetached"]
        except:
            print(f"{self.base_url}/addresses/{blockchain_id}/{address} failed")

    def get_account_refs(self, address, blockchain_id):
        r = requests.request("GET", f"{self.base_url}/addresses/{blockchain_id}/{address}?includeAccountRefs=true")

        if self.log_reponses:
            print(f"{r.status_code}: {r.text}")
        
        j = r.json()

        return j['accountRefs']

    def remove_none_fields(my_dict):
        return {
            key: value for key, value in my_dict.items()
            if value is not None
        }

if __name__ == "__main__":
    # COOKIE_VALUE = ""    
    # ams = AMS("test", cookie_value=COOKIE_VALUE)
    # print(json.dumps(ams.get_addresses(is_deposit=True, include_balances=True, limit=10, tags=["siba"]), indent=2))

    # print(ams.upsert_address(
    #         blockchain_id=2, 
    #         address="addr1q8034em76n4qyhfrexv8j349gpcr5904cc4fm9vf7le59wxlrtnha482qfwj8jvc09r22srs8g2lt332nk2cnalng2uqnnqh77", 
    #         is_pay=True
    #         # tags=["siba_loves_python"]
    #     ).text)
    # print(ams.get_addresses(account="1065010", limit=10))
    # print(ams.tag_address(address="addr1q8034em76n4qyhfrexv8j349gpcr5904cc4fm9vf7le59wxlrtnha482qfwj8jvc09r22srs8g2lt332nk2cnalng2uqnnqh77", blockchain_id=2, tag="HW🔥").text)
    # print(ams.detach_address(address="addr1q8034em76n4qyhfrexv8j349gpcr5904cc4fm9vf7le59wxlrtnha482qfwj8jvc09r22srs8g2lt332nk2cnalng2uqnnqh77", blockchain_id=2, account_ref="200064921008").text)
    
    # addresses = [
    #     "0xa05b8dd67114bedac493c8e79b8de6bc09b43d126f39b2a9e5e64401d7ea8fa3f24f06a766f37893314e7a8d89eed3c9"
    # ]
    # for address in addresses:
    #     r = ams.tag_address(address=address, blockchain_id=19, tag="stk-slashed")
    #     print(r.text)
    addresses = [
        ("addr1qyqhrfyev4qhkan0tlevfmcn6jfgfw63tdclux2kfm8e9g40u07gg2gmpqrchdhanz90vpcrx7c3gcjav47pcepw9t7sprmuwe", 2, "4fa51a86-df58-4744-a376-9b3a94c194ef")
    ]

    ENV = "test"
    LOCATION = "VAULT"
    COOKIE = "CfDJ8OX8hqrTQZFDgf5MKeHkP3HnsipE3j0rrji5J2PJ9taoxchGY10Uu9bryrtSntKI7-VfVl3XF_aDFAzZzd0shnvGMUFDP5SIWNzeo6-FnKU9sIknzgBMxw0JT1dVAwgjH4CqAoXHDztNN7Jw9uJWRu6ecRPtKGqrQTOIooPjqyiYtQ2kgxdn-mQF9BijdrW360UqSVZUqSce1ffAsR8_UAUc8cv1EPbYb32IVhDGEXkyHEqHuhUQp09uCpg0MQ6KpSWAHQuPU17Q19ZD6tVny9GBAGuSWR9Z_AHWCB5l-Un_DcDUxOP9qpeP92v6WCpcT_0ZSWMODNGnDz1oPm1V-vv8ZUaILurJBPvFmtC2h4Q-7O2_6y4siwG5elC1D6JF-h9KNreMgRDxwUN1RjaynCDYvLSkWgjcjOWJgiJ-J3PSJwoYE0_U6CsvJp8MMiktHXKkALe__nS2ZVX9uHdN4jNn1hc66UryPxTi2MVhcKskuCzgoD5UcDEa7v4ZsDygHzVQgVYgK4B-oM4vMxqDTac1n-3b9dCIPEQgSXvTSB9CO0DWtsU7fUAMfswDZa2mloMk-4JBw5U-pES5Qf6010qFxIuIVzU0nn8yrIqycl5rR6Lr8M_2lSEOJvIvigAIJ0rzatlDnXfJkEtml1tnYcjUfHit4sxVRcl_V38qQx9Qt1oIw1_DkJY1B4hM51g-NUJCI_8kOzGMAsLdyvBagAZ67ZTDw-JkQkbEqPPFYRMDO489gV9ggpf06mvgtN7xj1GsM5onqKe7rH-25u00virgyIc9ovITVmpewxQVANGRLit8yfja4aqjuZEfWEZU0KA9Jmwh1SJDdWmeRA8bQG0gc5j5CZjDDntaPtzdw5zqwwinbcsxTgMYFeHGYBVS7BS_dkSgr1a0NYeKzx17C-1PI-Jk4pV5oNX7FIn7-74XOjn1ibxbLKaWQCoNEQc1LaBIBud7lXNpc0fR_zlkQzgwKNCI14PjlizUZzLGcC2THBcnBsOMI2sSlAyHELKlR93ns-eB0MSTFlmwBOh0uI7J76jcHSODZ41x7sE9n1qqucQAveCH6ii7kXtco2q4XTxF81dGVx7nKucStsmOJYW7HKEo09jYDEaiNmJtSobd6tKxV4e-HAIs6qYz7V-AvpijTgme_h2dgjTVK8X5D7I78lL1YrLG75GBUx742xH1aKJGQuijvHmiT8l1KNwzk-O7Qtwen8GjW4WWr-6BNJgIOVRAs9ej7Gj2ywSabx218UszttN1VtrNGSMx4fpF6SpvYt-75icpjrVuV89HS6Etey_L4HEt0B7baihei45eTsYU2J6-QLgbPMtQ38B1MBVDQKK9WzMi6rPJETnoFQ6v0r2-unqIxcal0ScLTQm812fZmdxMyJgaA90rrermNWxYyj9zUSEdLVGOW6RcPvFROFs8NVg9zkUSfvUG-VoO_mIB-fXrNVfycCLWsJEtcxOKo1OWxMwoPugWtMgIcIwWjoCPgl8rYKhV6repmC5G13sMapVTu_d1yFqfbX0KtLff6-QSStjvNJGoJt4L5k3qd7yECq-GAjwGx99WDSviMQjgige3XppT6PvlkNllf0dkD0TpJoDvTH-A2ZNgujek-6ajStNAoOJ45sg69dFrhbTrBrXNKezfsbEEkbyMyt-Qi_TBwLlAeCNDB7GXci90FOuti1ZNQK6s-4Avq-SAlBNysJYN-YJ1VM4SMof69rRmPI06cBL0TbjrHd-R3-jwls1EXlx0IrIKSGqWZ46XYm5lVAnDFqxiSlWnpQL4Fe149Mt-3CMh-M7XmVgbBLULmgT7PwRH4IPEa9RMh4oWVwz7SrnZ2SSu--P5V9IXm3h-KhRaT_GYQYL7te_ENthFTKp5d9wHTW9jc_2tNkdgvY0mVfP_hzHtVOAPShLssfGKFjVCYnfDR5CxvwdLvc3CJrj3K46mxFd7SCRzqvVdr1qcS3PvAVqTOoPZaJGgGSCCvYnk5pIBoNRhzaKrTLIMH8Cqk7_dPj7XNTL-Ddkp5q_1W3ow-yt3o-XxLU7bBRa_ymMKJyPakZcZy6CQMewM4lij4Fo1D8JvWup_PHDKvRFCgGluMFweCODwPy-8ySoNRvqVeCzB2_WHO8iG5cue0B3Y9B3E1eTtLjMUWGcBmLqlG1y47r7IMrfB8xJZQ-H4YKYMWZJctl0pbW9Bbj4Ac6A2e0RyaVoTIWqjDYGWEtR0WEeNkmjK90U48RmZwcznwtJCukZsvHmJXVAxYG8W1XvCRq578S-cAPwNFUe946o_-u8sp4lXF2FhCO8RHuelBFwO-b_aarbxsPZqptd115S4kSJ3sXsimxTHePg8vWoHp6l-_Cs2qyY4lF7v84QSyafTILZBkUCbi2NT1cIPdxQq-KoL-uaVOD6pQVrsg3AhsDX1fC9eFRzTTTi7tLC_rjq-ieTM6qkEVJwvnYIT4jNzc1rSz27mj22ZVzmGCbTOdGwwa1O3VDsBvQWTpdbM5igs17cSKo2-xEXa5EtvNAzdz7Bg57CKuedl-vwq4Nr30q7wOTs8NMbJNxFN2Eb_M8fFpi5rq5wWJwStIMzXlme-A0anextMA4P_L64q0yrr2AyQaZtIaBndypWS3h4HB2FqkYXI2f7GCtATJsGTM8_bVQHKar5lUzdjLz42dNH2IRjNnip-rm0yQUWmUiDcjr3kJ6CkGckAGg0CvMvLeV1cHKEjsJvfQelm2TFr"
    TOTAL = len(addresses)
    ams = AMS(ENV, cookie_value=COOKIE)

    # print(json.dumps(ams.get_addresses(limit=1), indent=2))

    for i, address in enumerate(addresses):
        address, blockchain_id, vault_account_ref = address
        print(f"{i+1}/{TOTAL}: {address}")
        print(ams.tag_address(address=address, blockchain_id=2, tag="taggg").text)

        # print(ams.upsert_address(address=address, blockchain_id=blockchain_id, location=LOCATION, vault_account_ref=vault_account_ref).status_code)
        #print(ams.upsert_address(address=address, blockchain_id=blockchain_id, is_deposit=True).status_code)


