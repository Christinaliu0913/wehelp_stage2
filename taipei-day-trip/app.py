from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from pydantic import BaseModel
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源。如果需要限制来源，可以将 "*" 替换为特定来源。
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 建立資料庫類別設定
class Attraction(BaseModel):
	id: int
	name: str
	category: Optional[str]
	description: str
	address: Optional[str]
	transport: Optional[str]
	mrt: Optional[str]
	lat: float
	lng: float
	images: List[str]

class AttractionResponse(BaseModel):
	nextpage:Optional[int]
	data: List[Attraction]

class AttractionIDResponse(BaseModel):
	data: List[Attraction]

class MrtStationResponse(BaseModel):
	data: List
#連線至mysql 
db={
	"user":"root",
	"host":"localhost",
	"database":"taipei",
	"password":"ASdf1234."
}
def connect_sql():
	con = mysql.connector.connect(**db)
	return con

# Static Pages (Never Modify Code in this Block)
# 可加不可動！
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")

# 處理錯誤->導回首頁

### 當請求驗證錯誤的時候 
@app.exception_handler(RequestValidationError)
async def validation_exception(req: Request, exc: RequestValidationError):
	return RedirectResponse(url='/')

### 處理http異常
# @app.exception_handler(HTTPException)
# async def http_exception(req: Request, exc: HTTPException):
# 	if exc.status_code in {400, 422, 404}:
# 		return RedirectResponse(url='/')
# 	return JSONResponse(
# 		status_code=exc.status_code,
# 		content={
# 			"message":exc.detail
# 		},
# 	)
### 處理其他異常
@app.exception_handler(Exception)
async def global_exception(req: Request, exc: Exception):
	return RedirectResponse(url='/')

#API
#取得景點資料表
@app.get("/api/attractions",response_model=AttractionResponse)
async def get_attraction(page:int= Query(0, alias="page"), keyword:str=Query("",alias="keyword")):
	#keyword用來完全比對捷運站名稱、或模糊比對景點名稱的關鍵字，沒有給定則不做篩選
	try: 
		per_pageInfo=12 #每頁12筆資料
		offset = max(0, (page) * per_pageInfo) #mysql限制offset從第幾筆資料開始
		con=connect_sql()
		cursor=con.cursor(dictionary=True)#結果以字典形式返回

		#若是有輸入關鍵字的話 data
		if keyword:
			#transport 是direction
			query='''SELECT id, name, category, description, address, 
				transport, mrt, lat, lng, images FROM
				attraction WHERE name LIKE %s OR mrt LIKE %s
				LIMIT %s OFFSET %s 
				'''
			cursor.execute(query,(f'%{keyword}%',f'%{keyword}%',per_pageInfo,offset))
		else:
			query='''
				SELECT id, name, category, description, address, 
				transport, mrt, lat, lng, images FROM
				attraction LIMIT %s OFFSET %s
				'''
			cursor.execute(query,(per_pageInfo,offset))
		attractions= cursor.fetchall()
		#圖片部分格式化為List
		for attraction in attractions:
			if attraction["images"]:
				attraction["images"]= attraction['images'].split(',')
		#獲取總數據條目來計算下一頁 next page
		if keyword:
			cursor.execute(
				'''
				SELECT COUNT(*) As count FROM attraction WHERE name LIKE %s 
				''',(f'%{keyword}%',)
			)
		else:
			cursor.execute(
				'''
				SELECT COUNT(*) AS count FROM attraction
				'''
			)
		results= cursor.fetchone()['count']	
		#如果所有的項目不超過58項則顯示下一頁
		next_page= page+1 if offset+per_pageInfo < results else None
		response= {
			"nextPage":next_page,
			"data":attractions
		}
		return JSONResponse(response,status_code=200)
	except mysql.connector.Error: 
		return JSONResponse(content={"error":True,'message':'伺服器內部錯誤'},status_code=500)
	finally:
		cursor.close()
		con.close()

#取得景點編號取得景點資料
@app.get("/api/attraction/{attractionID}", response_model=AttractionIDResponse)
async  def get_attractionID(attractionID:int):
	try: 
		con=connect_sql()
		cursor=con.cursor(dictionary=True)
		cursor.execute(
			'''
			SELECT id, name, category, description, address, 
				transport, mrt, lat, lng, images FROM
				attraction WHERE id = %s
			''',(attractionID,)
		)
		attraction=cursor.fetchone()
		#錯誤訊息，請求無法正常處理的時候
		if not attraction:
			return JSONResponse(content={"error":True,"message":"景點編號不正確"},status_code=400)
		
		if attraction['images']:
			attraction['images']= attraction['images'].split(",")
		return JSONResponse(content={"data":attraction},status_code=200)
	except mysql.connector.Error:
		return JSONResponse(content={"error":True,'message':'伺服器內部錯誤'},status_code=500)
	finally: 
		cursor.close()
		con.close()


#取得所有捷運站名稱列表，按照周邊景點的數量由大到小排序
@app.get("/api/mrts", response_model=MrtStationResponse)
async def mrt_station():
	try:
		con=connect_sql()
		cursor=con.cursor(dictionary=True)
		cursor.execute(
			'''
			SELECT mrt, COUNT(*) as count FROM attraction 
			WHERE mrt IS NOT NULL AND mrt !=''
			GROUP BY mrt 
			ORDER BY count DESC
			'''
		)
		mrt_result =[row['mrt'] for row in cursor.fetchall()]
		if mrt_result: 
			return JSONResponse(content={"data":mrt_result},status_code=200)
	except mysql.connector.Error:
		return JSONResponse(content={"error":True, "message":"伺服器內部錯誤"})
	finally:
		con.close()
		cursor.close()

	

if __name__=='__main__':
	import uvicorn
	uvicorn.run(app, host='0.0.0.0', port=8000)