
import requests

from urllib.parse import quote


__version__ = "0.1"

__all__ = ["api"]

api_url = "https://nandha-api.onrender.com/"


class NandhaAPI:
     
         def __inint__(self) -> None:
              """Api for various purpose
    support group : NandhaSupport.t.me
    made by : NandhaBots.t.me
        """
             pass

         @staticmethod
         def imagine(query: str):
               """
               Generate AI Drawn images using prompt.
               Example:
                  from nandha-api import api
                  nandha = api.imagine('a cat')
                  print(nandha)
               """
              prompt = quote(query)
              end_point = f"imagine?prompt={prompt}"
              nandha = requests.get(api_url+end_point).json()
              return nandha

         @staticmethod
         def stylefont(text: str):
             """
             Get Stylish Text Fonts.
             Example:
                 from nandha-api import api
                 nandha = api.stylefont('nandha')
                 print(nandha)
             """
             prompt = quote(text)
             end_point = f"styletext?query={prompt}"
             nandha = requests.get(api_url+end_point).json()
             return nandha
           
         @staticmethod
         def run_code(code: str, lang: str):
              """
              Run Any Program Code.
              Example:
                 from nandha-api import api
                 nandha = api.run_code("print('hello')", "python")
                 print(nandha)
              """
              end_point = f"run?code={quote(code)}&language={lang}"
              nandha = requests.get(api_url+end_point).json()
              return nandha
           
         @staticmethod
         def zerochan(query: str):
             """
             Get images from zerochan.net
             Example:
                from nandha-api import api
                nandha = api.zerochan('miku')
                print(nandha)
             """
            prompt = quote(query)   
            end_point = f"zerochan?name={prompt}"
            nandha = requests.get(api_url+end_point).json()
            return nandha

          @staticmethod
          def couple():
              """
               Get couple pfp.
               Example:
                  from nandha-api import api
                  nandha = api.couple()
                  print(nandha)
              """
              end_point = "couples"
              nandha = requests.get(api_url+end_point).json()
              return nandha

          @staticmethod
          def guess():
              """
               Get random shuffled words.
               Example:
                  from nandha-api import api
                  nandha = api.guess()
                  print(nandha)
              """
              end_point = "guess"
              nandha = requests.get(api_url+end_point).json()
              return nandha

          @staticmethod
          def sof(query: str):
              """
               Get information from stackoverflow.
               Example:
                  from nandha-api import api
                  nandha = api.sof('python')
                  print(nandha)
              """
              prompt = quote(query)
              end_point = f"stackoverflow?query={prompt}"
              nandha = requests.get(api_url+end_point).json()
              return nandha
           
        
          @staticmethod
          def pit_video(url: str):
              """
               Get download url from pinterest video
               Example:
                  from nandha-api import api
                  nandha = api.pit_video('https://pin.it/7nW278MMD')
                  print(nandha)
              """
              end_point = f"vidpinterest?pinterest_url={url}"
              nandha = requests.get(api_url+end_point).json()
              return nandha       
               
          @staticmethod
          def pit_images(query: str):
              """
               Get pinterest images with query
               Example:
                  from nandha-api import api
                  nandha = api.pit_images('gojo')
                  print(nandha)
              """
              prompt = quote(query)
              end_point = f"pinterest?query={prompt}"
              nandha = requests.get(api_url+end_point).json()
              return nandha  

          @staticmethod
          def reverse(url: str):
              """
               Get google reverse image.
               Example:
                  from nandha-api import api
                  nandha = api.couple()
                  print(nandha)
              """
              end_point = f"reverse?img_url={url}"
              nandha = requests.post(api_url+end_point).json()
              return nandha    





api = NandhaAPI()
