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


from .base import ApiException


class UnpaidBill(ApiException):
    code = 9000
    message = "You have an unpaid bill, so you can't create another one"


class InvalidPaymentState(ApiException):
    code = 9001
    message = "Invalid payment state. Available: {all}"


class PaymentCantBeCancelled(ApiException):
    code = 9002
    message = "Payment with id {id} can't be cancelled: payment already paid, cancelled or expired"


class PromocodeExpired(ApiException):
    code = 9003
    message = "Entered promocode expired"


class PromocodeIsNotAvailableForYourCurrency(ApiException):
    code = 9004
    message = 'Promocode is not available for your currency'


class InvalidPromocodeType(ApiException):
    code = 9005
    message = 'Invalid promocode type. Available: {all}'
