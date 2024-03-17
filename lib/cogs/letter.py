import re
import json
import os

import discord
from discord.ext.commands import Cog, command, Context
import requests
import base64
import hashlib
import PyPDF2

from lib.bot import Bot


class LXPApi:
    def __init__(self, user, token):
        self.user = user
        self.token = token
        self.url = "https://api.letterxpress.de/v2"

    def _check_pdf_file(self, file_path: str) -> bool:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found")
        if not file_path.endswith(".pdf"):
            raise ValueError(f"File {file_path} is not a PDF file")
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            if len(reader.pages) != 1:
                raise ValueError(f"File {file_path} has {len(reader.pages)} pages, but only 1 page is allowed")
            width, height = reader.pages[0].mediabox.upper_right
            a4_width, a4_height = 595, 842
            margin = 5
            if abs(width - a4_width) > margin or abs(height - a4_height) > margin:
                raise ValueError(
                    f"File {file_path} has not the correct size (A4): {width}x{height} instead of {a4_width}x{a4_height}")
        return True

    def _pdf_to_base64(self, file_path: str) -> (str, str):
        with open(file_path, "rb") as file:
            base64_pdf = base64.b64encode(file.read()).decode()
        md5_hash = hashlib.md5(base64_pdf.encode()).hexdigest()
        return base64_pdf, md5_hash

    def _get_authorized(self, url: str, data: dict = None, test: bool = True) -> dict:
        if data is None:
            data = {}
        headers = {
            "Content-Type": "application/json"
        }
        data["auth"] = {
            "username": self.user,
            "apikey": self.token,
            "mode": "test" if test else "live"
        }
        response = requests.get(url, headers=headers, json=data)
        return response.json()

    def _post_authorized(self, url: str, data: dict = None, test: bool = True) -> dict:
        if data is None:
            data = {}
        headers = {
            "Content-Type": "application/json"
        }
        data["auth"] = {
            "username": self.user,
            "apikey": self.token,
            "mode": "test" if test else "live"
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def get_balance(self) -> str:
        url = f"{self.url}/balance"
        response = self._get_authorized(url)
        balance = f"{response['data']['balance']} {response['data']['currency']}"
        return balance

    def get_price(self) -> str:
        url = f"{self.url}/price"
        response = self._get_authorized(url, data={
            "letter": {
                "specification": {
                    "pages": 1,
                    "color": "1",
                    "mode": "simplex",
                    "shipping": "national",
                }
            }
        })
        price = f"{response['data']['price']} EUR"
        return price

    def send_letter(self, pdf_file_path: str, test: bool = True) -> int:
        self._check_pdf_file(pdf_file_path)
        url = f"{self.url}/printjobs"
        base64_file, md5_hash = self._pdf_to_base64(pdf_file_path)
        print(base64_file)
        response = self._post_authorized(url, data={
            "letter": {
                "base64_file": base64_file,
                "base64_file_checksum": md5_hash,
                "filename_original": os.path.basename(pdf_file_path),
                "specification": {
                    "color": "1",
                    "mode": "simplex",
                    "shipping": "national",
                }
            }
        }, test=test)
        return response["data"]["id"]

    def check_letter(self, letter_id: int) -> str:
        url = f"{self.url}/printjobs/{letter_id}"
        response = self._get_authorized(url)
        beautified_json = json.dumps(response, indent=4)
        return beautified_json


class Letter(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.lxp_api = LXPApi(self.bot.config.letterxpress_user, self.bot.config.letterxpress_token)

    def escape_latex(self, text):
        latex_special_chars = {
            '#': r'\#',
            '$': r'\$',
            '%': r'\%',
            '^': r'\^',
            '&': r'\&',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '\\': r'\textbackslash{}'
        }
        for char, escape in latex_special_chars.items():
            if char != '\\':  # Handle backslashes separately
                text = text.replace(char, escape)
        text = re.sub(r'(?<!\\)\\(?!textbackslash{})', latex_special_chars['\\'], text)
        return text

    def create_pdf(self, sender_name: str, sender_street: str, sender_street_nr: int, sender_post_code: int,
                   sender_city: str,
                   recipient_name: str, recipient_street: str, recipient_street_nr: int, recipient_post_code: int,
                   recipient_city: str,
                   text: str, file_path: str):
        with open("template.tex", "r") as tex_template_file:
            tex_template = tex_template_file.read()

        tex_template = tex_template.replace("$FROM_NAME$", self.escape_latex(sender_name))
        tex_template = tex_template.replace("$FROM_STREET$", self.escape_latex(sender_street))
        tex_template = tex_template.replace("$FROM_STREET_NR$", self.escape_latex(str(sender_street_nr)))
        tex_template = tex_template.replace("$FROM_POST_CODE$", self.escape_latex(str(sender_post_code)))
        tex_template = tex_template.replace("$FROM_CITY$", self.escape_latex(sender_city))
        tex_template = tex_template.replace("$TO_NAME$", self.escape_latex(recipient_name))
        tex_template = tex_template.replace("$TO_STREET$", self.escape_latex(recipient_street))
        tex_template = tex_template.replace("$TO_STREET_NR$", self.escape_latex(str(recipient_street_nr)))
        tex_template = tex_template.replace("$TO_POST_CODE$", self.escape_latex(str(recipient_post_code)))
        tex_template = tex_template.replace("$TO_CITY$", self.escape_latex(recipient_city))
        tex_template = tex_template.replace("$TEXT$", self.escape_latex(text))

        letter_tex = tex_template
        with open(file_path, "w") as letter_tex_file:
            letter_tex_file.write(letter_tex)
        os.system(f"pdflatex -output-directory /tmp {file_path}")

    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Letter enabled!")

    @command()
    async def letter(self, ctx: Context, *, params):
        if not params:
            await ctx.send("`!letter status`")
            await ctx.send("`!letter track <id>`")
            await ctx.send("`!letter <sender_name> <sender_street> <sender_street_nr> <sender_post_code> "
                           "<sender_city> <recipient_name> <recipient_street> <recipient_street_nr> "
                           "<recipient_post_code> <recipient_city> <text>`")
            return
        params = params.split(" ")
        if len(params) == 1 and params[0] == "status":
            balance = self.lxp_api.get_balance()
            price = self.lxp_api.get_price()
            await ctx.send(f"current balance: {balance}, current price per letter: {price}")
            return

        if len(params) == 2 and params[0] == "track":
            letter_id = int(params[1])
            status = self.lxp_api.check_letter(letter_id)
            await ctx.send(f"```{status}```")
            return

        if len(params) != 11:
            await ctx.send("`!letter <sender_name> <sender_street> <sender_street_nr> <sender_post_code> "
                           "<sender_city> <recipient_name> <recipient_street> <recipient_street_nr> "
                           "<recipient_post_code> <recipient_city> <text>`")
            return

        pdf_path = "/tmp/letter.pdf"
        self.create_pdf(params[0], params[1], int(params[2]), int(params[3]), params[4],
                        params[5], params[6], int(params[7]), int(params[8]), params[9], params[10], pdf_path)
        letter_id = self.lxp_api.send_letter(pdf_path, test=True)
        await ctx.send(f"Letter sent with id {letter_id}")


def setup(bot):
    bot.add_cog(Letter(bot))
