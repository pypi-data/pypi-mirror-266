from fastapi import Depends
from fastapi_cache.decorator import cache

from fastgenerateapi import APIView, DeleteTreeView, GetTreeView
from fastgenerateapi.deps import paginator_deps
from middlewares.jwt_middleware.schemas import UserObject
from modules.example.models import StaffInfo, CompanyInfo
from modules.example.schemas import CompanyInfoRead, CompanyInfoCreate, ListTestSchema, StaffReadSchema


class CompanyView(APIView, DeleteTreeView, GetTreeView):
    model_class = CompanyInfo
    # schema = CompanyInfoRead
    # create_schema = CompanyInfoCreate

    @cache()
    async def view_get_list(self, paginator=Depends(paginator_deps())) -> ListTestSchema:

        return await self.pagination_data(queryset=self.queryset, fields=["id", "name"], paginator=paginator)


class StaffView(APIView):

    def __init__(self):
        self.model_class = StaffInfo
        self.order_by_fields = ["-created_at"]
        self.prefetch_related_fields = {"company": ["name"]}
        # self.router_args = {
        #     # "view_get_staff_list": ListTestSchema
        #     "view_get_staff_list": TestSchema
        # }
        self.get_all_schema = StaffReadSchema
        # self.dependencies = [Depends(ADG.authenticate_user_deps), ]
        super().__init__()

    # async def get_one(self, pk: str, *args, **kwargs) -> Union[BaseModel, dict, None]:
    #     print(datetime.datetime.now())
    #     data = await super().get_one(pk=pk, *args, **kwargs)
    #     result = create_staff.delay()
    #     print(result.id)
    #     print(datetime.datetime.now())
    #     return data

    # async def view_get_staff_list(self, name: Optional[str] = None):
    #     conn = Tortoise.get_connection("default")
    #     # conn = Tortoise.get_connection("local")
    #     val = await conn.execute_query_dict("SELECT * FROM information_schema.columns WHERE TABLE_NAME = 'staffinfo'")
    #     # val = await conn.execute_query_dict("SELECT * FROM staffinfo")
    #     print(val)
    #     return self.success(data={"data_list": val})

    @cache()
    async def view_get_staff_list(
            self,
            paginator=Depends(paginator_deps()),
            # current_user: UserObject = Depends(ADG.authenticate_user_deps),
    ) -> ListTestSchema:
        data = await self.pagination_data(queryset=self.queryset, fields=["id", "name"], paginator=paginator)
        return self.success(data=data)


# class StaffView(SQLGetAllView):
#     table_name = "staffinfo"











