const getTokenURL = '/api/user/auth' 
const token = this.localStorage.getItem('token');//從local端獲取token

//-------------------load---------------------------|

window.addEventListener('load',function(){
    //確認登入情形
    checkSigned();

    //獲取景點id訊息
    const attractionId = getAttractionIdFromURL();

    if(attractionId){
        console.log(`Attraction ID1: ${attractionId}`);
        AttractionIdAPI(attractionId);
    }else{
        console.log('not valid attractionID')
        window.location.href = '/'
    }
    
});

//|------------------登入/註冊-----------------------|

 //左右滑動
 function moveLeft(){
    document.getElementById('mrts-list').scrollLeft -= 450;
  }
  function moveRight(){
    document.getElementById('mrts-list').scrollLeft += 450;
  }
  //登入頁面
  function signIn(){
    document.querySelector('#signin').style.display = 'flex';
    document.querySelector('.overlay').style.display = 'flex';
    document.querySelector('#signup').style.display = 'none';
  }
  //返回
  function signinClose(){
    document.querySelector('#signin').style.display = 'none';
    document.querySelector('.overlay').style.display = 'none';
  }
  //註冊頁面
  function signUp(){
    document.querySelector('#signin').style.display = 'none';
    document.querySelector('#signup').style.display = 'flex';
    document.querySelector('.overlay').style.display = 'flex';
  }
  function signupClose(){
    document.querySelector('#signup').style.display = 'none';
    document.querySelector('.overlay').style.display = 'none';
  }

  //登入後navigationbar變動
  function Showsigned(){
    document.getElementById('nav-signin').style.display = 'none';
    document.getElementById('nav-signout').style.display = 'flex';
  }
  function signOut(){
    localStorage.removeItem('token');
    alert('成功登出！');
    document.getElementById('nav-signin').style.display = 'flex';
    document.getElementById('nav-signout').style.display = 'none';
  }
//註冊送出表單
  function signUpAPI(){
    const signUpName = document.getElementById('signUpName').value.trim();
    const signUpEmail = document.getElementById('signUpEmail').value.trim();
    const signUpPassword = document.getElementById('signUpPassword').value.trim();
    const errorMessage = document.getElementById('signUpError');
    //檢查是否所有格子已填寫
    if(!signUpName || !signUpEmail || !signUpPassword){
      alert('請填妥所有資訊');
      errorMessage.textContent = '';
      return;
    }

    fetch('/api/user',{
      method: "POST",
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({name:signUpName,email:signUpEmail,password:signUpPassword})
    }).then(res => {return res.json()}).then(result =>{
      //若是fetch到回覆error，則出現提示字樣
      if(result.error){
        errorMessage.textContent = '';
        errorMessage.textContent = result.message;
      }else{
        alert('註冊成功!');
        //清空輸入框和錯誤消息
        document.querySelector('#signup-form').reset();
        errorMessage.textContent = '';
      }
    }).catch(error => {
      errorMessage.textContent = error.message;
      console.error("Error:",error)
    })
  }
//登入
function signInAPI(){
  const signInEmail = document.getElementById('signInEmail').value.trim();
  const signInPassword = document.getElementById('signInPassword').value.trim();
  const signInError = document.getElementById('signInError')
  //清理錯誤訊息
  signInError.textContent = '';

  if(!signInEmail || !signInPassword){
    alert('請填入帳號與密碼');
    signInError.textContent = '';
    return ;
  }

  fetch('/api/user/auth',{
    method: "PUT",
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({email:signInEmail,password:signInPassword})
  }).then(res => {
    if(!res.ok){
      signInError.textContent = '';
      signInError.textContent =  res.message;
      }
    return res.json();
  }).then(result =>{
    if(result.error){
      signInError.textContent = '';
      signInError.textContent =  result.message;
    }else{
      //將token儲存至localStorage
      localStorage.setItem('token', result.token)
      alert('成功登入！');
      signinClose();
      Showsigned();
      document.querySelector('#signin-form').reset();
      signInError.textContent = '';
    }
  }).catch(error =>{
    console.log('Error:', error);
    signInError.textContent = error.error;
  })
    
}

//檢查是否登入狀態
async function checkSigned(){
  if (!token){
    console.log('not signed in');
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
    }else{
      console.error('Failed to verify login', await tokenRes.json());
      localStorage.removeItem('token');//驗證失敗，清除不正確的token
    }
  }catch(error){
      console.error('Error:',error);
      alert('加油好嗎？');
    }
  
};

//---------attraction單頁page------------------|


//---------費用切換更新--------

function ChooseFee(){
    const feeElement = document.querySelector('#fee');
    const morningCheck = document.querySelector('#morning');
    const afternoonCheck = document.querySelector('#afternoon');

    if(morningCheck.checked){
        feeElement.textContent = '新台幣2000元';
    }else if(afternoonCheck.checked){
        feeElement.textContent = '新台幣2500元';
    }else{
        feeElement.textContent = '新台幣2000元';
    }
}
//---------景點資料的獲取-----



//獲取URL中景點ID
function getAttractionIdFromURL(){
    const attractionURLId = window.location.pathname.split('/');
    return attractionURLId[attractionURLId.length - 1];
}
//fetch Attractionid的API
function AttractionIdAPI(Id){
    const attractionURL =`/api/attraction/${Id}`
    console.log(`Attraction ID: ${attractionURL}`)
    fetch(attractionURL).then(res =>{
            return res.json()
        }).then(result =>{
            attractionIdData(result);
        }).catch(error=>{
            window.location.href = '/';
            console.log("fail to fetch attractionID:",error);
        });
}

//取得attractionId的內容
function attractionIdData(data){
const attractionData = data.data;
const attractionId = attractionData.id;
const attractionName = attractionData.name;
const attractionCat = attractionData.category;
const attractionMrt = attractionData.mrt;
const attractionDes = attractionData.description;
const attractionAddress = attractionData.address;
const attractionImg = attractionData.images;
const attractionTransport = attractionData.transport;
attractionInfo(attractionName,attractionCat,attractionMrt);
attractionIMG(attractionImg);
attractionDetail(attractionDes,attractionAddress,attractionTransport)
}

function attractionInfo(name,cat,mrt){
//上方景點名稱、種類、捷運站
const attractionInfoDiv = document.querySelector('.attraction-intro-info-upper');

const attractionInfoName = document.createElement('h3');
attractionInfoName.classList.add('attraction-intro-info-title');
attractionInfoName.textContent = name;

const attractionInfoCatMrt = document.createElement('div');
attractionInfoCatMrt.classList.add('attraction-intro-info-content');
attractionInfoCatMrt.textContent = `${cat} at ${mrt}`;

attractionInfoDiv.appendChild(attractionInfoName);
attractionInfoDiv.appendChild(attractionInfoCatMrt);
}
//下方說明欄
function attractionDetail(description,address,transportation){
const attractionDetailDesDiv = document.querySelector('.description');
const attractionDetailAddressDiv = document.querySelector('.address');
const attractionDetailTransDiv = document.querySelector('.transpor');

const attractionDetailDes = document.createElement('p');
attractionDetailDes.textContent = description;

const attractionDetailAddress = document.createElement('p');
attractionDetailAddress.textContent = address;

const attractionDetailtransport = document.createElement('p');
attractionDetailtransport.textContent = transportation;

attractionDetailDesDiv.appendChild(attractionDetailDes);
attractionDetailAddressDiv.appendChild(attractionDetailAddress);
attractionDetailTransDiv.appendChild(attractionDetailtransport);
}

//---------圖片輪播功能-------------------------|

function attractionIMG(imgs){
    const attractionIMGContainerDiv = document.querySelector('.attraction-intro-img-container');
    const attractionIMGIndicatorsDiv = document.querySelector('.attraction-intro-img-indicators');

    imgs.forEach((img,index)=>{
        //設置照片
        const carouselIMG = document.createElement('div')
        carouselIMG.classList.add('attraction-intro-img-carouselIMG');
        carouselIMG.style.backgroundImage = `url(${img})`
        if(index === 0){
            carouselIMG.classList.add('active');//讓第一張照片active
        }

        attractionIMGContainerDiv.appendChild(carouselIMG);

        //加入下方球球
        const carouselIndicator = document.createElement('div');
        carouselIndicator.classList.add('attraction-intro-img-indicator');
        if(index === 0){
            carouselIndicator.classList.add('active');
        }

        carouselIndicator.setAttribute('indicator-index',index)//設定每個球球的編號
        carouselIndicator.addEventListener('click', () => changeIMGbyIndicator(index));

        attractionIMGIndicatorsDiv.appendChild(carouselIndicator);
    })  
}

let currentIMGIndex = 0;//將index預設為第一張

function showIMG(index){
    const carouselIMGs = document.querySelectorAll('.attraction-intro-img-carouselIMG');
    const carouselIndicators = document.querySelectorAll('.attraction-intro-img-indicator');
    if (index >= carouselIMGs.length){//實現輪播的功能-> 超過照片組數時，循環到第一張照片
        currentIMGIndex = 0
    }else if(index < 0){//再看看
        currentIMGIndex = carouselIMGs.length -1;
    }else{
        currentIMGIndex = index;
    }

    carouselIMGs.forEach((img,index) =>{
        img.classList.toggle('active', index === currentIMGIndex);
    })
    carouselIndicators.forEach((indicator,index) =>{
        indicator.classList.toggle('active', index === currentIMGIndex)
    })
};

//用球球換照片
function changeIMGbyIndicator(index){
    showIMG(index)
}

//向左右滑一張照片
function imgLeft(){
    showIMG(currentIMGIndex - 1);
};
function imgRight(){
    showIMG(currentIMGIndex + 1);
};
