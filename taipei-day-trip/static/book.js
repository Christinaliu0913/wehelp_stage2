const getTokenURL = '/api/user/auth' 
const token = localStorage.getItem('token');//從local端獲取token
const bookingURL = '/api/booking'
//-------------------load---------------------------|
window.addEventListener('load',function(){
    //確認登入情形
    checkSigned();
    bookForm();
});

//|------------------登入/註冊-----------------------|
 
  //登入後navigationbar變動
  function Showsigned(){
    document.getElementById('nav-signin').style.display = 'none';
    document.getElementById('nav-signout').style.display = 'flex';
  }
  function signOut(){
    localStorage.removeItem('token');
    alert('成功登出！');
    window.location.href='/';
  }


//檢查是否登入狀態
async function checkSigned(){
    if (!token){
      window.location.href='/'
      return;//直接返回
    }

    try{
      const tokenRes = await fetch(getTokenURL,{
        method: 'GET',
        headers:{
          'Authorization' : `Bearer ${token}` //發送token進行驗證
        }
      })
      if(tokenRes.ok){
        const tokenResult = await tokenRes.json();
        Showsigned();
        console.log("Login verified:", tokenResult);
        localStorage.setItem('user_data', JSON.stringify(tokenResult.data))
      }else{
        console.error('Failed to verify login', await tokenRes.json());
        localStorage.removeItem('token');//驗證失敗，清除不正確的token
      }
    }catch(error){
        console.error('Error:',error);
        alert('加油好嗎？');
      }
    
  };

//---------------fetch預定的資料-------------
function bookForm(){
    fetch(bookingURL,{
        'method':'GET',
        'headers': {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(res=>res.json())
    .then(result => {
        renderBook(result);
    })
    .catch(error => {
        alert(error.message)
    })
}

function renderBook(bookData){
    console.log(bookData)
    if(bookData.data !== null){
        const attractionData = bookData.data.attraction
        const bookDatas = bookData.data
        const userData = JSON.parse(localStorage.getItem('user_data'))
        const username = userData.name;//獲取用戶名
        const user_email = userData.email;//獲取用戶email
        //介紹
        document.getElementById('username').textContent=`您好，${username}，待預定的行程如下：`
        //景點名稱
        document.querySelector('.info-detail-title').textContent = `台北一日遊：${attractionData.name}`;
        //日期
        document.querySelector('#bookDate').textContent = bookDatas.date;
        //時間
        document.querySelector('#bookTime').textContent = bookDatas.time;
        //價格
        document.querySelector('#bookFee').textContent = bookDatas.price;
        document.querySelector('#sumupPrice').textContent = `總價：新台幣${bookDatas.price}元`
        //圖片
        document.querySelector('.info-img').style.backgroundImage = `url(${attractionData.image})`
        //地址
        document.querySelector('#attractionAddress').textContent = attractionData.address;
        document.querySelector('input[name="name"]').value = username;
        document.querySelector('input[name="email"]').value = user_email
    }else{
        document.querySelector('#main').innerHTML= '';
        document.querySelector('#noBooking').textContent = '目前沒有任何待預定的行程';
    }
    

}

//刪除資料
function deleteBooking(){
    fetch(bookingURL,{
        method:'DELETE',
        headers:{
            'Authorization': `Bearer ${token}`
        }
    })
    .then(res => res.json())
    .then(result => {
        if(result.ok){
            alert('已刪除預定行程');
            location.reload();
        }else{
            alert(result.message)
        }
    })
    .catch(error => {
        alert(error.message)
    })
}
    
