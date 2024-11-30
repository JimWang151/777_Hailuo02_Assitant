# Made by JimWang for ComfyUI
# 02/04/2023

import torch
import random
import folder_paths
import uuid
import json
import urllib.request
import urllib.parse
import os
import numpy as np

import comfy.utils
from comfy.cli_args import args

from PIL import Image, ImageOps, ImageSequence, ImageFile
from PIL.PngImagePlugin import PngInfo
import collections
from torchvision.transforms import ToPILImage,ToTensor
import torchvision.transforms as T

from PIL import Image, ImageDraw

import collections
import xml.etree.ElementTree as ET




class GetPrompt:
        def __init__(self):
            pass

        @classmethod
        def INPUT_TYPES(s):
            return {
                "required": {
                    "character": ("STRING", {"multiline": True,  "tooltip": "The text to be encoded."}),
                    "width": ("INT",{"default": 512}),
                    "height": ("INT",{"default": 512}),
                    "step": ("INT", {"default": 1}),
                    "tid": ("INT", {"default": 1}),
                },
            }

        RETURN_TYPES = ("STRING","STRING",)
        RETURN_NAMES = ("name","prompt",)
        FUNCTION = "refine"
        OUTPUT_NODE = True
        CATEGORY = "Hailuo02"
        DESCRIPTION = "Generate prompt."

        def refine(self,width,height,step,character,tid):
            # 初始化画布高度和宽度

            prompt="raw photo,"
            id="template"+str(tid)
            closeup="close-up1"
            version="man"
            first_10_chars = character[:10]
            if "woman" in first_10_chars or "girl" in first_10_chars:
                version = "woman"
            resolution=str(width)+"×"+str(height)
            if width==768 and height==512 and step % 2==0:
                closeup="close-up2"
            if height==1024 and width==1024:
                closeup = "half body"
            if height==1024 and width ==768:
                closeup = "full body"
            prompt+=self.getShotStyle(step,width,height)
            # 返回结果
            prompt+=self.getAperture(step,width,height)


            prompt += self.getFocalLength(step,width, height)
            print(f"pa1:{id}")
            print(f"pa2:{version}")
            print(f"pa3:{resolution}")
            print(f"pa4:{closeup}")
            name,tempprompt=self.getPrompt(id,version,resolution,closeup)
            prompt+=prompt+character+","+tempprompt
            print(f"final prompt: {prompt}")
            return (name,prompt)

        def getShotStyle(self,step,width,height):
            # 获取镜头类型
            result = ""  # 初始化结果字符串为空
            if height==1024 :
                result="full body shot,perspective Compression,"
            # 检查是否满足特定的条件，并追加相应的字符串
            if width == 1024 and step % 2 == 0:  # 检查step是否可以被2整除
                result += " ,"
            if width == 768 and height == 512:
                result = "(half body:1.3),"
                if step % 2 ==0:
                    result="Close-up portrait,"
            # 返回结果
            return result


        def getAperture(self,step, width,height,round=1):
            # 获取光圈
            result=""
            if height == 1024:
                result="f/10,"
            if height == 1024 and width ==1024 :
                result = "f/5.6-f8,"
            if width == 768 and height == 512 :
                result = "f/11,"
                if step % 2 ==0:
                    result ="f/3-f/6,"
            # 返回结果
            return result

        def getFocalLength(self,step, width,height,round=1):
            # 获取焦距
            result = ""
            if height == 1024:
                result=",50mm,"
                if height == 1024 and width == 1024:
                    result = ",85mm,"
            if width == 768 and height == 512 :
                result = ",85mm,"
                if step % 2 ==0:
                    result =",200mm,"
            # 返回结果

            return result

        def getPrompt(self,template_id, version, resolution, closeup="close-up1"):
            # 解析XML文件
            # 获取当前文件的目录
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # 构建 XML 文件的相对路径
            xml_file_path = os.path.join(current_dir, 'data', 'template.xml')

            # 读取 XML 文件
            tree = ET.parse(xml_file_path)
            #tree = ET.parse('./template.xml')
            root = tree.getroot()

            # 遍历所有template节点
            for template in root.findall('template'):
                # 检查template的id是否匹配
                if template.get('id') == template_id:
                    # 获取template下的version节点
                    version_node = template.find('version')
                    if version_node is not None and version_node.text == version:
                        # 遍历template下的所有details节点
                        for details in template.findall('details'):
                            # 检查resolution是否匹配
                            resolution_node = details.find('resolution')
                            if resolution_node is not None and resolution_node.text == resolution:
                                # 检查closeup是否匹配
                                desc_node = details.find('desc')
                                if desc_node is not None and desc_node.text == closeup:
                                    # 获取name和prompt
                                    name = template.find('name').text
                                    prompt = details.find('prompt').text
                                    return name, prompt

            # 如果没有找到匹配的节点，返回None
            return "未指定模板", ","
