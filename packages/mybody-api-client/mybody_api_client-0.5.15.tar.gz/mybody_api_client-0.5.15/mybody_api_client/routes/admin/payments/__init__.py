#
# (c) 2024, Yegor Yakubovich, yegoryakubovich.com, personal@yegoryakybovich.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from mybody_api_client.routes.admin.payments.methods import AdminPaymentMethodRoute
from mybody_api_client.utils import BaseRoute, RequestTypes


class AdminPaymentRoute(BaseRoute):
    prefix = '/payments'

    methods = AdminPaymentMethodRoute()

    async def create(
            self,
            account_service_id: int,
            service_cost_id: int,
            payment_method: str,
            payment_method_currency_id: int,
            promocode: str = None,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/create',
            parameters={
                'account_service_id': account_service_id,
                'service_cost_id': service_cost_id,
                'payment_method': payment_method,
                'payment_method_currency_id': payment_method_currency_id,
                'promocode': promocode,
            },
            response_key='id',
        )

    async def update(
            self,
            id_: int,
            state: str = None,
            data: str = None,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/update',
            parameters={
                'id': id_,
                'data': data,
                'state': state,
            },
        )

    async def delete(
            self,
            id_: int,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/delete',
            parameters={
                'id': id_,
            },
        )

    async def cancel(
            self,
            id_: int,
    ):
        return await self.request(
            type_=RequestTypes.POST,
            prefix='/cancel',
            parameters={
                'id': id_,
            },
        )

    async def get(self, id_: int):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/get',
            parameters={
                'id': id_,
            },
            response_key='payment',
        )

    async def get_list(self, account_service_id: int):
        return await self.request(
            type_=RequestTypes.GET,
            prefix='/list/get',
            parameters={
                'account_service_id': account_service_id,
            },
            response_key='payments',
        )
