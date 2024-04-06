"""
Type annotations for verifiedpermissions service client paginators.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_verifiedpermissions/paginators/)

Usage::

    ```python
    from boto3.session import Session

    from mypy_boto3_verifiedpermissions.client import VerifiedPermissionsClient
    from mypy_boto3_verifiedpermissions.paginator import (
        ListIdentitySourcesPaginator,
        ListPoliciesPaginator,
        ListPolicyStoresPaginator,
        ListPolicyTemplatesPaginator,
    )

    session = Session()
    client: VerifiedPermissionsClient = session.client("verifiedpermissions")

    list_identity_sources_paginator: ListIdentitySourcesPaginator = client.get_paginator("list_identity_sources")
    list_policies_paginator: ListPoliciesPaginator = client.get_paginator("list_policies")
    list_policy_stores_paginator: ListPolicyStoresPaginator = client.get_paginator("list_policy_stores")
    list_policy_templates_paginator: ListPolicyTemplatesPaginator = client.get_paginator("list_policy_templates")
    ```
"""

from typing import Generic, Iterator, Sequence, TypeVar

from botocore.paginate import PageIterator, Paginator

from .type_defs import (
    IdentitySourceFilterTypeDef,
    ListIdentitySourcesOutputTypeDef,
    ListPoliciesOutputTypeDef,
    ListPolicyStoresOutputTypeDef,
    ListPolicyTemplatesOutputTypeDef,
    PaginatorConfigTypeDef,
    PolicyFilterTypeDef,
)

__all__ = (
    "ListIdentitySourcesPaginator",
    "ListPoliciesPaginator",
    "ListPolicyStoresPaginator",
    "ListPolicyTemplatesPaginator",
)

_ItemTypeDef = TypeVar("_ItemTypeDef")

class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """

class ListIdentitySourcesPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/verifiedpermissions.html#VerifiedPermissions.Paginator.ListIdentitySources)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_verifiedpermissions/paginators/#listidentitysourcespaginator)
    """

    def paginate(
        self,
        *,
        policyStoreId: str,
        filters: Sequence[IdentitySourceFilterTypeDef] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...,
    ) -> _PageIterator[ListIdentitySourcesOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/verifiedpermissions.html#VerifiedPermissions.Paginator.ListIdentitySources.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_verifiedpermissions/paginators/#listidentitysourcespaginator)
        """

class ListPoliciesPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/verifiedpermissions.html#VerifiedPermissions.Paginator.ListPolicies)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_verifiedpermissions/paginators/#listpoliciespaginator)
    """

    def paginate(
        self,
        *,
        policyStoreId: str,
        filter: PolicyFilterTypeDef = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...,
    ) -> _PageIterator[ListPoliciesOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/verifiedpermissions.html#VerifiedPermissions.Paginator.ListPolicies.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_verifiedpermissions/paginators/#listpoliciespaginator)
        """

class ListPolicyStoresPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/verifiedpermissions.html#VerifiedPermissions.Paginator.ListPolicyStores)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_verifiedpermissions/paginators/#listpolicystorespaginator)
    """

    def paginate(
        self, *, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListPolicyStoresOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/verifiedpermissions.html#VerifiedPermissions.Paginator.ListPolicyStores.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_verifiedpermissions/paginators/#listpolicystorespaginator)
        """

class ListPolicyTemplatesPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/verifiedpermissions.html#VerifiedPermissions.Paginator.ListPolicyTemplates)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_verifiedpermissions/paginators/#listpolicytemplatespaginator)
    """

    def paginate(
        self, *, policyStoreId: str, PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListPolicyTemplatesOutputTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/verifiedpermissions.html#VerifiedPermissions.Paginator.ListPolicyTemplates.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_verifiedpermissions/paginators/#listpolicytemplatespaginator)
        """
