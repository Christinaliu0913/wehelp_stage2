 //左右滑動
 function moveLeft(){
    document.getElementById("mrts-list").scrollLeft -= 450;
  }
  function moveRight(){
    document.getElementById("mrts-list").scrollLeft += 450;
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
    document.querySelector('#signin').style.display = "none";
    document.querySelector('#signup').style.display = "flex";
    document.querySelector('.overlay').style.display = 'flex';
  }
  function signupClose(){
    document.querySelector('#signup').style.display = 'none';
    document.querySelector('.overlay').style.display = 'none';
  }

  //------------------KeywordSearch-----------------------

  //防止搜尋關鍵字時重載更新頁面
  document.getElementById('search-form').addEventListener('submit',function(event){
    event.preventDefault();
    keywordSearch();
  });


  //關鍵字搜尋
  function keywordSearch(){
    const keyword = document.getElementById('search-keyword').value.trim();
    const attractionsDiv = document.querySelector('.attraction-box');
    attractionsDiv.innerHTML='';//清空目前的景點卡面
    nextPage =null;//重置下一頁

    if(keyword !==''){
      const keywordURL = `/api/attractions?keyword=${encodeURIComponent(keyword)}`;
      fetch(keywordURL).then(res=>res.json()).then(result=> {
        attractionsAPI(result);
        nextPage=result.nextPage;
        if(observe)observe.disconnect();
          setupInfiniteScroll();//重新設置無限滾動
        }).catch(error=>{
          console.error('Error searching attractions:', error);
        })
    }else{
      fetch(attractionsURL).then(res=>res.json()).then(result=> {
        attractionsAPI(result);
        nextPage=result.nextPage;
        if(observe)observe.disconnect();
          setupInfiniteScroll();//重新設置無限滾動
        }).catch(error=>{
          console.error('Error searching attractions:', error);
        })

    }
  };



  //----------------attractions-----------------------
  //取得attractions 資訊
  let nextPage = null;
  const attractionsURL='/api/attractions'
  window.addEventListener('load',function(){
    fetch(attractionsURL).then(res=>{
      return res.json();
    }).then(result =>{
      attractionsAPI(result);
      //保存下一頁的值
      nextPage = result.nextPage;
      //設置無限滾動
      setupInfiniteScroll();
    }).catch(error => {
      console.error('Error fetching attractions:', error);
    });
  });

  //----------------設置無限滾動
  function setupInfiniteScroll(){
    const observe = new IntersectionObserver(entries=>{
      if(entries[0].isIntersecting && nextPage !== null){
        loadMoreAttractions();
      }
    },{
     rootMargin: '0px 0px -10px 0px'// 提前100pxload下一頁
    });
    observe.observe(document.querySelector('.footer'));//觀察到footer後
  }
  //載入更多圖片
  function loadMoreAttractions(){
    const nextPageURL = `/api/attractions?page=${nextPage}`;
    fetch(nextPageURL)
      .then(res=>{
        return res.json();
      }).then(result =>{
        attractionsAPI(result);
        nextPage = result.nextPage;//更新下一頁的值
        if (nextPage==null){
          observe.disconnect();//最後一頁停止觀察
        }
      }).catch(error => {
        console.error('Error fetching next page of attractions:', error);
      });
  }
  //----------------attractionsCard-----------------------------
  function attractionsAPI(data){
    const attractionsData = data.data;
    const attractionsDiv = document.querySelector('.attraction-box')
    for(let i=0;i < attractionsData.length;i++){
      const attractionItem = attractionsData[i];
      const attractionsIMG = attractionItem.images;
      const attractionsName = attractionItem.name;
      const attractionsCat = attractionItem.category;
      const attractionsMrt = attractionItem.mrt;
      attractionsCard(attractionsDiv,attractionsIMG,attractionsName,attractionsCat,attractionsMrt)
    }
  }
  function attractionsCard(parentDiv,imgs,name,cat,mrt){
    //景點卡片
    const attractionsCard = document.createElement("div");
    attractionsCard.classList.add('attraction-card');
    //若第一張
    const img = new Image();
    img.src =imgs[0];
    let imgIndex = 0;
    img.onerror= function(){
      imgIndex++;
      if(imgIndex < imgs.length){
        img.src = imgs[imgIndex];
      };
    };
    img.onload = function(){
      attractionsCard.style.backgroundImage= `url(${img.src})`;
    }

    
    //景點卡片內容
    const attractionsCardBox = document.createElement('div');
    attractionsCardBox.classList.add('attraction-card-box');

    //景點卡片標題-名稱
    const attractionsCardItem1 = document.createElement('div');
    attractionsCardItem1.classList.add('attraction-card-item1');

    const attractionsCardItem1P = document.createElement('p')
    attractionsCardItem1P.textContent = name;

    //景點卡片標題-捷運、分類
    const attractionsCardItem2 = document.createElement('div');
    attractionsCardItem2.classList.add('attraction-card-item2');

    const attractionsCardItem2P1 = document.createElement('p');
    attractionsCardItem2P1.classList.add('loc');
    attractionsCardItem2P1.textContent = mrt;

    const attractionsCardItem2P2 = document.createElement('p');
    attractionsCardItem2P2.classList.add('cat');
    attractionsCardItem2P2.textContent = cat;
    
    //appendChild
    parentDiv.appendChild(attractionsCard)
    attractionsCard.appendChild(attractionsCardBox);
    attractionsCardBox.appendChild(attractionsCardItem1)
    attractionsCardBox.appendChild(attractionsCardItem2)
    attractionsCardItem1.appendChild(attractionsCardItem1P)
    attractionsCardItem2.appendChild(attractionsCardItem2P1)
    attractionsCardItem2.appendChild(attractionsCardItem2P2)
  }


  //----------------MRT---------------------
  //取得mrt資訊
  const mrtsURL='/api/mrts'
  fetch(mrtsURL).then(res=>{
    return res.json();
  }).then(result =>{
    mrtsAPI(result)
  }).catch(error=>{
    console.error('Error fetching mrts:',error);
  });

  //mrt資訊
  function mrtsAPI(data){
    const mrtData = data.data;
    const mrtDiv = document.querySelector('#mrts-list')
    for(let i=0; i < mrtData.length; i++){
      const mrtItem = mrtData[i];
      mrtsList(mrtDiv,mrtItem);
    }
  }

  //----------------mrt-List
  function mrtsList(parentDiv,mrt){
    const mrtListItem = document.createElement('div');
    mrtListItem.classList.add('listBar-mrt-item');
    mrtListItem.textContent = mrt;
    mrtListItem.addEventListener('click', function(){
        document.getElementById('search-keyword').value = mrt;
        keywordSearch();//觸發搜尋
    })
    parentDiv.appendChild(mrtListItem)
  }

