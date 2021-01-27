######################################################################
##        Copyright (c) 2021 Carsten Wulff Software, Norway
## ###################################################################
## Created       : wulff at 2021-1-20
## ###################################################################
##  The MIT License (MIT)
##
##  Permission is hereby granted, free of charge, to any person obtaining a copy
##  of this software and associated documentation files (the "Software"), to deal
##  in the Software without restriction, including without limitation the rights
##  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
##  copies of the Software, and to permit persons to whom the Software is
##  furnished to do so, subject to the following conditions:
##
##  The above copyright notice and this permission notice shall be included in all
##  copies or substantial portions of the Software.
##
##  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
##  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
##  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
##  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
##  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
##  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
##  SOFTWARE.
##
######################################################################

import yaml
import click
import svgwrite
import numpy as np
import pandas as pd
import re


class PinList():
    def __init__(self,category):
        self.category = category

    def color(self,name):
        for c in self.category:
            if(re.search(c["regex"],name)):
               return c["color"]
        return "black"

    def iotype(self,name):

        for c in self.category:
            if(re.search(c["regex"],name)):
               return c["type"]
        return "io"
    


class SvgQfn(svgwrite.Drawing):

    def isOptionFalse(self,name):
        if(name in self.options and self.options[name] == False):
            return True
        else:
            return False

    def isOptionTrue(self,name):
        if(name in self.options and self.options[name] == False):
            return False
        else:
            return True

    
    def __init__(self,x_org,y_org,width,height,step,svg_file,pins,options,**args):
        self.options = options
        self.x = x_org
        self.y = y_org
        self.width = width
        self.height = height
        self.step = step
        self.x_center = self.x + width/2
        self.y_center =  self.y + height/2
        self.font_size_text = width/8
        self.font_size_pin = self.font_size_text/4
        self.data = list()
        self.pins = pins
        super().__init__(svg_file,profile='tiny',**args)

    def qfn_box(self,name,title):
        gr = svgwrite.container.Group()

        gr.add(self.rect((self.x,self.y),(self.width,self.height),fill="none",stroke="black",stroke_width=3))
        gr.add(self.text(title,
                         insert=(self.x_center,self.y_center),text_anchor="middle",font_family="Arial",font_size=self.font_size_text))

        if(self.isOptionTrue("packagetext")):
            gr.add(self.text(name,
                             insert=(self.x_center,self.y_center+self.font_size_text),text_anchor="middle",font_family="Arial",font_size=self.font_size_text*3/4))
        return gr

    def addPinToDf(self,name,nr):

        io_type = self.pins.iotype(name)

        self.data.append([nr,name,io_type])


    def qfn_pin(self,x,y,name,location,nr=0):
        gr = svgwrite.container.Group()

        x_next = x
        y_next = y
        nr_next = nr
        
        xtn = x 
        ytn = y
        xt = xtn
        yt = ytn

        fsp= self.font_size_pin

        xr = x
        yr = y
        wr = fsp
        hr = fsp

        rotate = True
        if(location == "top"):
            text_anchor = "start"
            x_next -= self.step
            ytn -= self.font_size_pin/2
            yt -= self.font_size_pin*2.5
            xr = x- fsp/2
            wr = fsp
            yr = y 
            hr = fsp*2
            nr_next+=1

        elif(location == "bottom"):
            text_anchor = "end"
            x_next -= self.step
            ytn += self.font_size_pin/2
            yt += self.font_size_pin*2.5
            xr = x- fsp/2
            wr = fsp
            yr = y-fsp*2
            hr = fsp*2
            nr_next-=1
        elif(location == "right"):
            text_anchor = "start"
            y_next += self.step
            rotate = False
            xtn += self.font_size_pin*0.5
            xt += self.font_size_pin*2.5
            xr = x- fsp*2
            wr = fsp*2
            yr = y-fsp/2
            hr = fsp
            nr_next-=1
        elif(location == "left"):
            text_anchor = "end"
            y_next += self.step
            rotate = False
            xtn -= self.font_size_pin*0.5
            xt -= self.font_size_pin*2.5
            xr = x
            wr = fsp*2
            yr = y-fsp/2
            hr = fsp
            nr_next+=1
        if(rotate):
            transform = 'rotate(270,%s, %s)'
            xtn += fsp/2
            xt += fsp/2
        else:
            transform = 'rotate(0,%s, %s)' 
            ytn += self.font_size_pin/2
            yt += self.font_size_pin/2

        t_nr = self.text(str(nr),
                         insert=(xtn,ytn),
                         font_family="Arial",
                         font_size=self.font_size_pin,
                         text_anchor=text_anchor,
                         transform=transform % (xtn,ytn)
        )
        if(self.isOptionTrue("number")):
            gr.add(t_nr)

        r = self.rect((xr,yr),(wr,hr),fill="white",stroke="black",stroke_width=1)
        gr.add(r)

        tcolor =  self.pins.color(name)
        if(re.search("^\s*NC",name)):
            tcolor = "lightgray"

        gr.add(self.text(name,
                         insert=(xt,yt),
                         font_family="Arial",
                         font_size=self.font_size_pin,
                         fill=tcolor,
                         text_anchor=text_anchor,
                         transform=transform % (xt,yt)
        ))

        return (gr,x_next,y_next,nr_next)

    def qfn_pins(self,x,y,step,pins_per_side,location,anchor,pins):
        gr = svgwrite.container.Group()
        N = len(pins)
        if location == "top" and anchor == "right":
            xi = x + pins_per_side*step + step*1
            yi = y
            nr = pins_per_side*3+1
        elif location == "bottom" and anchor == "right":
            xi = x + pins_per_side*step + step*1
            yi = y + self.height
            nr = pins_per_side*2
        elif location == "right"  and anchor =="top":
            xi = x +self.width
            yi = y + step*2
            nr = pins_per_side*3
        elif location == "left"  and anchor =="top":
            xi = x
            yi = y + step*2
            nr = 1

        for i in range(0,pins_per_side):
            if i < N:
                self.addPinToDf(pins[i],nr)
                (pin,xi,yi,nr) =  self.qfn_pin(xi,yi,pins[i],location,nr=nr)
                gr.add(pin)

        return gr


@click.command()
@click.argument("YAML_FILE")
def pacgen(yaml_file):
    with open(yaml_file,"r") as fi:
        ym = yaml.safe_load(fi)

    svg_file = yaml_file.replace(".yaml",".svg")
    csv_file = yaml_file.replace(".yaml",".csv")

    scale= ym["scale"]
    step = ym["pitch"]*scale

    width = ym["width"]*scale
    height = ym["height"]*scale
    pins_per_side = int(ym["pins"]/4)

    svgwidth = width*1.8
    svgheight = height*1.8

    x_org = (svgwidth - width)/2
    y_org = (svgheight - height)/2

    pins = None
    if("category" in ym):
        pins = PinList(ym["category"])

    options = dict()
    if("options" in ym):
        options = ym["options"]
        
    #- Init file
    svg = SvgQfn(x_org,y_org,width,height,step,svg_file,pins,options,size=(svgwidth,svgheight))

    
    
    #- Print pins
    for key in ("top","bottom","left","right"):
        pins = ym[key]["pins"]
        if(pins == None):
            continue

        svg.add(svg.qfn_pins(x_org,y_org,step,pins_per_side,key,ym[key]["anchor"],pins))

    #- Add QFN box
    svg.add(svg.qfn_box(ym["package"] + str(ym["pins"]) + "_" + str(ym["width"]) + "x" + str(ym["height"]),ym["title"]))

    #- Save SVG
    svg.save()

    #- Save pinlist
    df = pd.DataFrame(svg.data,columns=["nr","name","type"])
    df = df.set_index("nr")
    df = df.sort_values(by=["nr"], ascending=True)
    df.to_csv(csv_file)


if __name__ == "__main__":
    pacgen()
