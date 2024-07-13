const getTokenURL = '/api/user/auth' 
const token = localStorage.getItem('token');//從local端獲取token

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
        method:'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    })
    .then(res=>res.json())
    .then(result => {
        console.log(result)
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
    


//-------------TapPay設定與串接----------------------

//初始化，從後台獲取專案ID,api token

TPDirect.setupSDK(
  151966,
  'app_1QnD3OTAcbpXSZiXnvUsPUvaC8fm51s2LWVHzzuOXiZpRrfwbtzzPzh5Qnlo',
  'sandbox'
);

//設置信用卡表單

TPDirect.card.setup({
  fields: {
    number:{
      element:'#card-number',
      placeholder: '**** **** **** ****'
    },
    expirationDate:{
      element:'#card-expiration-date',
      placeholder: 'MM/YY'
    },
    ccv:{
      element: '#ccv',
      placeholder: 'CCV'
    }
  },
  styles: {
    'input': {
        'color': '#a6a6a6',
        'font-size': '14px'
    },
    ':focus': {
        'color': 'blue'
    },
    '.valid': {
        'color': 'green'
    },
    '.invalid': {
        'color': 'red'
    },
    '@media screen and (max-width: 400px)': {
        'input': {
            'color': 'orange'
        }
    }
  }
});



//用於更新狀態的函數，可以根據需要擴展
function updateStatus(status){
  console.log('status', status);
}
  


//表單提交

document.getElementById('reserve-button').addEventListener('click',function(event){
  event.preventDefault();

  
  //確認所有格子填妥
  const name = document.getElementById('user-name').value.trim();
  const email = document.getElementById('user-email').value.trim();
  const phone = document.getElementById('user-phone').value.trim();
 
  //取得TapPay fields 的status
  const tappayStatus = TPDirect.card.getTappayFieldsStatus()
  //確認是否可以 GetPrime
  if (tappayStatus.canGetPrime === false || !name || !email || !phone){
    alert('請填妥完整資訊');
    console.log('TapPay fields Status:', tappayStatus)
    return
  }

  //Get Prime

  TPDirect.card.getPrime(async function(result){
    if (result.status !== 0){
      alert('取得Token失敗: ' +result.msg)
      console.log('Error:', result);
      return;
    }
    alert('get prime成功，prime'+result.card.prime)
    //將prime傳送到sever端
    const prime = result.card.prime;
    sendPrimeToSever(prime);

  });
});

const bookingURL = '/api/booking'
const orderURL = '/api/orders'

//將prime傳送到sever端
async function sendPrimeToSever(prime){
    const setPrime = prime
    //獲取會員資料
    const userData = JSON.parse(localStorage.getItem('user_data'))
    const userName = userData.name;//獲取用戶名
    const userEmail = userData.email;//獲取用戶email
    const userPhone = document.querySelector('#user-phone').value.trim()//獲取用戶手機

    
    //獲取景點資料
    const bookingResponse = await fetch(bookingURL,{
      method:'GET',
      headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
      }
    });

    if(!bookingResponse.ok){
      throw new Error('failed to fetch booking data')
    }else{
      console.log('success to fetch booking')
    }

    const result = await bookingResponse.json();

    console.log(result);
    const attractionData = result.data.attraction;
    const attractionId = attractionData.id;
    const attractionName = attractionData.name;
    const attractionAddress = attractionData.address;
    const attractionImg = attractionData.image;
    const bookDate = result.data.date;
    const bookTime = result.data.time;
    const bookPrice = result.data.price;

    const bookingForm = {
      prime: setPrime,
      order: {
        price: bookPrice,
        trip:{
          attraction:{
            attractionId: attractionId,
            name: attractionName,
            address: attractionAddress,
            image: attractionImg
          },
          date: bookDate,
          time: bookTime
        },
        contact: {
          name: userName,
          email: userEmail,
          phone: userPhone
        }
      }
    }
    console.log(bookingForm);
    postOrder(bookingForm);
};


//---------------------------
function postOrder(bookingForm){
  console.log('sending JSON', JSON.stringify(bookingForm));
  fetch('/api/orders',{
    method: "POST",
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(bookingForm)
  }).then(req => 
    req.json()
  ).then(result =>{
    if(result.error){
      alert(result.message);
      console.log(result.message);
      return;
    }else{
      alert('訂購成功')
      console.log(result.detail)
    }
    console.log(result)
  }).catch(error => {
  alert(error.message)
  console.log('Error:',error)
  })
}


