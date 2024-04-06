import importlib
import io
import operator
import os
import time
import uuid
from pathlib import Path
from typing import List, Union, Dict, Type, Tuple, Optional

from fastapi import UploadFile
from pydantic import create_model, ValidationError, BaseModel
from starlette._utils import is_async_callable
from starlette.background import BackgroundTask
from starlette.responses import StreamingResponse, FileResponse
from tortoise.models import Model
from tortoise.queryset import QuerySetSingle

from fastgenerateapi.schemas_factory.common_schema_factory import common_schema_factory


class ToolMixin:

    @staticmethod
    def reserve_dict(data: dict) -> dict:
        """
        字典key,value互转
        """
        result = {}
        for key, val in data:
            result[val] = key
        return result

    async def export_xlsx(
            self,
            model_list: Model,
            headers: List[str],
            fields: List[str],
            fields_handler: dict,
            file_save_path: Optional[str] = None,
            # rpc_param: Union[Dict[str, Dict[str, List[str]]], Type[RPCParam], None] = None,
            title: str = None,
            modules: str = "openpyxl"
    ) -> StreamingResponse:
        limit_modules = ["openpyxl", "xlsxwriter"]
        if modules not in limit_modules:
            return self.error(msg=f"export xlsx modules only import {'、'.join(limit_modules)}")
        try:
            wb = importlib.import_module(modules).Workbook()
        except Exception:
            return self.error(msg=f"please pip install {modules}")
        if modules == "openpyxl":
            def write(sh, row, col, value):
                sh.cell(row, col).value = value

            start_col = 1
            start_row = 1
        else:
            def write(sh, row, col, value):
                sh.write(row, col, value)

            start_col = 0
            start_row = 0
        try:
            sh = wb.active
            sh.title = title if title else f'{self.model_class._meta.table_description}'

            for col, header in enumerate(headers, start_col):
                write(sh, start_row, col, header)

            for row, model in enumerate(model_list, start_row + 1):
                model = await self.getattr_model(model=model, fields=fields)
                # model = await self.setattr_model_rpc(self.model_class, model, rpc_param)

                for col, field in enumerate(fields, 1):
                    info = getattr(model, field, "")
                    handler = fields_handler.get(field)
                    if handler and hasattr(handler, "__call__"):
                        if is_async_callable(handler):
                            info = await handler(info)
                        else:
                            info = handler(info)
                    write(sh, row, col, info)
        finally:
            if file_save_path:
                wb.save(file_save_path)
                return self.success(msg="请求成功")
            bytes_io = io.BytesIO()
            wb.save(bytes_io)
            bytes_io.seek(0)

        return StreamingResponse(
            bytes_io,
            media_type="application/vnd.ms-excel;charset=UTF-8",
        )

    async def export_pdf(
            self,
            model: Model,
            fields_list: List[List[Union[str, Tuple[str]]]],
            data: List[List[str]],
            # rpc_param: Union[Dict[str, Dict[str, List[str]]], Type[RPCParam], None] = None,
            font: str = "msyh",
            font_path: str = None,
            modules: str = "fpdf"
    ) -> StreamingResponse:
        """
        fields_list: [["名字", ("name", "名字"), (数据库字段， 字段中文名)], [第二行]]

        """
        limit_modules = ["fpdf"]
        if modules not in limit_modules:
            return self.error(msg=f"export xlsx modules only import {'、'.join(limit_modules)}")
        try:
            pdf = importlib.import_module(modules).FPDF()
        except Exception:
            return self.error(msg=f"please pip install {modules}")
        pdf.add_page()
        pdf.add_font(font, '', font_path if font_path else f"../font/{font}.ttf", True)
        pdf.set_font(font, '', 8)
        if data:
            for data_row in data:
                data_row_width = 180 / len(data_row)
                for data_col in data_row:
                    pdf.cell(data_row_width, 8, data_col)
                pdf.ln(10)
        else:
            async def write(model_single_obj):
                fields_data = []
                for fields in fields_list:
                    for field in fields:
                        if type(field) == tuple:
                            fields_data.append(field[0])
                model_data = await self.getattr_model(model_single_obj, fields_data)
                # model_data = await self.setattr_model_rpc(self.model_class, model_data, rpc_param)
                for fields in fields_list:
                    cell_width = 180 / len(fields)
                    for field in fields:
                        if type(field) == str:
                            msg = f"{field[1]}"
                        else:
                            msg = f"{field[1]} {getattr(model_data, field[0]) if getattr(model_data, field[0]) else ''}"
                        pdf.cell(cell_width, 8, msg)
                    pdf.ln(10)

            if type(model) == QuerySetSingle:
                await write(model)
            else:
                for model_obj in model:
                    await write(model_obj)
                    pdf.add_page()
        byte_string = pdf.output(dest="S").encode('latin-1')
        bytes_io = io.BytesIO(byte_string)

        return StreamingResponse(
            bytes_io,
            media_type="application/pdf"
        )

    async def import_xlsx(
            self,
            file: UploadFile,
            file_save_path: str,
            headers: List[str],
            # [
            #        "name",
            #       ("is_male", {"男"： True, "女": False} 或者 方法, {"额外字段"： 方法}, ...),
            # ]
            # 方法(默认传excel的值)
            fields: List[Union[str, dict, tuple, list]],
            combine_fields: Optional[List[Dict[str, any]]] = None,
            model_class: Optional[Type[Model]] = None,
            create_schema: Optional[Type[BaseModel]] = None,
            # storage_path: Union[str, Path],
            # rpc_param: Union[Dict[str, Dict[str, List[Union[str, tuple]]]], Type[RPCParam]] = None,
            is_delete: Optional[bool] = True,
            modules: str = "openpyxl",
    ) -> StreamingResponse:
        """
        fields: 方法(默认传excel的值)
        例如：
        [
            "name",    # 传入值是 name 字段的值
            ("is_male", {"男"： True, "女": False} 或者 方法, {"额外字段"： 方法}, ...),
            # 值 "男" 获取为bool值，不在字典里为None, 页可以自定义 同步或异步方法 获取值
        ]
        """
        limit_modules = ["openpyxl"]
        if modules not in limit_modules:
            return self.error(msg=f"export xlsx modules only import {'、'.join(limit_modules)}")

        if not file:
            return self.fail(msg=f"请先选择合适的文件")

        if not model_class:
            model_class = self.model_class
        if not create_schema:
            create_schema = common_schema_factory(model_class, name=f"{model_class.__name__}ExcelImportSchema")
        res = await file.read()
        with open(file_save_path, 'wb') as destination:
            destination.write(res)
        try:
            wb = importlib.import_module(modules).load_workbook(file_save_path, read_only=True, data_only=True)
        except Exception:
            return self.error(msg=f"please pip install {modules}")
        try:
            ws = wb.active

            header_row = ws[1]
            header_list = []
            for msg in header_row:
                header_list.append(str(msg.value).replace(" ", ''))

            if len(header_list) != len(headers):
                return self.fail(message="文件首行长度校验错误")

            if not operator.eq(header_list, headers):
                return self.fail(message="文件首行内容校验错误")

            # if ws.max_row < 2:
            #     return self.fail(msg="导入数据不能为空")

            create_list = []
            effective_row = 0
            for row in range(2, ws.max_row + 1):
                data = {}
                # data_schema = {}
                row_data = ws[row]
                if await self.excel_row_is_empty(row_data):
                    continue
                effective_row += 1
                for col, field_input in enumerate(fields):
                    if type(field_input) in [str, int]:
                        data[field_input] = row_data[col].value
                        # data_schema[field_input] = (type(row_data[col].value), ...)

                    if type(field_input) == tuple or type(field_input) == list:
                        key = field_input[0]
                        val = field_input[1]
                        required_doc = {}
                        if len(field_input) > 2:
                            required_doc = field_input[2]
                            if required_doc == "required":
                                required_doc = {"required": True}
                        if type(val) == dict:
                            model_val = val.get(row_data[col].value)
                            if not model_val and required_doc.get("required"):
                                return self.fail(
                                    msg=required_doc.get("error",
                                                         "") or f"第{row}行{self.get_field_description(key)}不能为空")
                            data[key] = model_val
                            # data_schema[key] = (type(model_val), ...)
                        elif hasattr(val, "__call__"):
                            if is_async_callable(val):
                                model_val = await val(row_data[col].value)
                            else:
                                model_val = val(row_data[col].value)
                            data[key] = model_val
                            # data_schema[key] = (type(model_val), ...)
                        else:
                            raise NotImplemented
                    else:
                        raise NotImplemented
                for combine_field in combine_fields:
                    field = combine_field.get("field", None)
                    value = combine_field.get("value", None)
                    function = combine_field.get("function", None)
                    args = combine_field.get("args", None)
                    if not field or (not function and not value):
                        continue
                    if value:
                        data[field] = value
                    else:
                        if not args:
                            if is_async_callable(function):
                                model_val = await function()
                            else:
                                model_val = function()
                        else:
                            args_list = []
                            for arg in args:
                                args_list.append(data.get(arg, ""))
                            if is_async_callable(function):
                                model_val = await function(*args_list)
                            else:
                                model_val = function(*args_list)
                        data[field] = model_val
                try:
                    create_obj = model_class(**create_schema(**data).dict(exclude_unset=True))
                except ValidationError as e:
                    error_field = e.errors()[0].get('loc')[0]
                    description = self.get_field_description(error_field)
                    if not data.get(error_field):
                        return self.fail(message=f"第{row}行{description}不能为空")
                    return self.fail(message=f"第{row}行{description}填写错误")
                await self.check_unique_field(create_obj, model_class=model_class)
                create_list.append(create_obj)

            await model_class.bulk_create(create_list)
        finally:
            wb.close()
        if effective_row == 0:
            return self.fail(message="导入数据不能为空")
        if is_delete:
            return self.success(
                msg='创建成功',
                background=BackgroundTask(lambda: os.remove(file_save_path))
            )
        return self.success(msg='创建成功')

    @staticmethod
    async def excel_row_is_empty(row_list) -> bool:
        is_empty = True
        for row in row_list:
            if row.value is not None:
                return False

        return is_empty

    async def excel_model(
            self,
            headers: List[str] = None,
            model_class: Optional[Model] = None,
            excel_model_path: Optional[str] = None,
            modules: str = "openpyxl",
            title: Optional[str] = None,
    ) -> Union[FileResponse, StreamingResponse]:
        if excel_model_path:
            return FileResponse(
                path=excel_model_path,
                filename="导入模板.xlsx",
                media_type="xlsx",
            )

        limit_modules = ["openpyxl", "xlsxwriter"]
        if modules not in limit_modules:
            return self.error(msg=f"export xlsx modules only import {'、'.join(limit_modules)}")
        try:
            wb = importlib.import_module(modules).Workbook()
        except Exception:
            return self.error(msg=f"please pip install {modules}")
        if modules == "openpyxl":
            def write(sh, row, col, value):
                sh.cell(row, col).value = value

            start_col = 1
            start_row = 1
        else:
            def write(sh, row, col, value):
                sh.write(row, col, value)

            start_col = 0
            start_row = 0
        try:
            sh = wb.active
            sh.title = title if title else f'{model_class._meta.table_description}'

            for col, header in enumerate(headers, start_col):
                write(sh, start_row, col, header)

        finally:
            bytes_io = io.BytesIO()
            wb.save(bytes_io)
            bytes_io.seek(0)

        return StreamingResponse(
            bytes_io,
            media_type="application/vnd.ms-excel;charset=UTF-8",
        )





