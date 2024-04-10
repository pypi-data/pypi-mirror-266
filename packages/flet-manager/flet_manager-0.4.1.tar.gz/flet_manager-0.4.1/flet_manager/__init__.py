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


from flet_core import Page
from flet import app

from .utils import Client, Themes
from .utils import Font
from .views import MainView, ErrorView


class AppType:
    FLET = 'flet'
    FASTAPI = 'fastapi'


class App:
    routes: dict[str]
    client: Client

    def __init__(
            self,
            name: str = 'Flet Manager',
            view_main=MainView,
            view_error=ErrorView,
            views: list = None,

            themes: Themes = Themes(),
            fonts: list[Font] = None,

            **kwargs,
    ):
        self.view_main = view_main
        self.view_error = view_error
        self.themes = themes

        if not fonts:
            fonts = []
        self.fonts = dict(zip([font.name for font in fonts], [font.path for font in fonts]))

        if not views:
            views = []
        self.routes = {}
        for view in views:
            self.routes[view.route] = view

        self.fastapi = app(
            self.start,
            export_asgi_app=True,
            **kwargs,
        )

    async def start(self, page: Page):
        self.client = Client(
            page=page,
            themes=self.themes,
            fonts=self.fonts,
            routes=self.routes,
            view_main=self.view_main,
            view_error=self.view_error,
        )
        await self.client.change_view(
            view=self.view_main(),
        )
