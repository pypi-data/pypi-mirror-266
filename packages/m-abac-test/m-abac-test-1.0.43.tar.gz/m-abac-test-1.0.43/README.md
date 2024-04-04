### ABAC Engine
Thư viện xử lý kiểm tra quyền theo logic ABAC (Attribute-based access control).


### Cài đặt:
```bash
 $ pip3 install m-abac
 ```

### Sử dụng:

##### Kiểm tra user có quyền thao tác hay không:
   ```python
    from mobio.libs.abac import PolicyDecisionPoint
    resource = "deal"
    # action = "UpdateFromSale"
    action = "ListFromSale"

    pdb = PolicyDecisionPoint(resource=resource, action=action)
    result = pdb.is_allowed()
    if not result.get_allow_access():
        # trả về lỗi không có quyền truy cập 
   ```
#### Log - 1.0.0
    - release sdk
#### Log - 1.0.2
    - update sdk
#### Log - 1.0.3
    - update cache
#### Log - 1.0.4
    - update cache
#### Log - 1.0.5
    - mm-dd operator
    - update if exists
#### Log - 1.0.6
    - update operator exists
#### Log - 1.0.7
    - format date string using parse, string ignore case, accept check value None