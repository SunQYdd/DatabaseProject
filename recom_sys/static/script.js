document.addEventListener('DOMContentLoaded', function() {
    const tabs = document.querySelectorAll('.tab-btn');
    const sections = document.querySelectorAll('.content-section');
    const loadingElement = document.createElement('div');
    loadingElement.className = 'loading';
    loadingElement.textContent = '加载中...';
    
    // 标签映射 (Frontend tag key -> Backend tag ID)
    const TAG_MAP = {
        'science-fiction': 1,
        'mystery': 2,
        'growth': 3,
        'classic': 4,
        'romance': 5,
        'history': 6
    };

    // 顶部用户操作区域
    const header = document.querySelector('.header');
    let userActions = document.querySelector('.user-actions');
    
    // 如果 HTML 中没有 user-actions (兼容旧版), 则创建并添加到 header
    if (!userActions) {
        userActions = document.createElement('div');
        userActions.className = 'user-actions';
        header.appendChild(userActions);
    }
    
    // 1. 个人信息按钮容器
    const profileContainer = document.createElement('div');
    profileContainer.className = 'profile-container';
    
    // 个人按钮
    const profileBtn = document.createElement('button');
    profileBtn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
        个人
    `;
    profileBtn.className = 'profile-btn';
    profileBtn.title = '个人中心';
    
    // 下拉菜单
    const profileMenu = document.createElement('div');
    profileMenu.className = 'dropdown-menu'; // 使用 style.css 中的 dropdown-menu
    
    const menuItems = [
        { text: '个人信息', icon: '👤', action: () => { window.location.href = '/profile'; } },
        { text: '我的收藏', icon: '❤️', action: () => showFavorites() }
    ];
    
    menuItems.forEach(item => {
        const btn = document.createElement('button');
        btn.className = 'dropdown-item'; // 使用 style.css 中的 dropdown-item
        btn.innerHTML = `<span style="margin-right: 8px">${item.icon}</span>${item.text}`;
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            item.action();
            profileMenu.classList.remove('show');
        });
        profileMenu.appendChild(btn);
    });
    
    // 组装个人区域
    profileContainer.appendChild(profileBtn);
    profileContainer.appendChild(profileMenu);
    userActions.appendChild(profileContainer);

    // 个人按钮点击事件
    profileBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        profileMenu.classList.toggle('show');
    });

    // 点击外部关闭菜单
    document.addEventListener('click', function(e) {
        if (profileMenu.classList.contains('show') && !profileContainer.contains(e.target)) {
            profileMenu.classList.remove('show');
        }
    });
    
    // 2. 登出按钮
    const logoutBtn = document.createElement('button');
    logoutBtn.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
        登出
    `;
    logoutBtn.className = 'logout-btn';
    
    logoutBtn.addEventListener('click', function() {
        fetch('/api/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/login';
            }
        })
        .catch(error => {
            console.error('登出失败:', error);
        });
    });
    userActions.appendChild(logoutBtn);

    function showFavorites() {
        // 隐藏其他部分
        sections.forEach(section => section.classList.remove('active'));
        tabs.forEach(btn => btn.classList.remove('active'));
        
        // 显示收藏部分
        const favoritesSection = document.getElementById('favorites');
        if (favoritesSection) {
            favoritesSection.classList.add('active');
            loadFavorites();
        }
    }

    function loadFavorites() {
        const container = document.getElementById('favorites').querySelector('.items-grid');
        container.innerHTML = '';
        container.appendChild(loadingElement.cloneNode(true));

        fetch('/api/user/favorites')
            .then(response => {
                if (response.status === 401) {
                    window.location.href = '/login';
                    return;
                }
                return response.json();
            })
            .then(result => {
                container.innerHTML = '';
                if (result.code === 200 && result.data.records.length > 0) {
                    result.data.records.forEach(item => {
                        const card = createItemCard(item, item.type);
                        card.addEventListener('click', () => {
                            window.location.href = `/detail/${item.type}/${item.itemId}`;
                        });
                        container.appendChild(card);
                    });
                } else {
                    container.innerHTML = '<div class="no-results">暂无收藏内容</div>';
                }
            })
            .catch(error => {
                console.error('加载收藏失败:', error);
                container.innerHTML = '<div class="error">加载失败</div>';
            });
    }
    
    // 为添加按钮添加事件监听器
    document.querySelectorAll('.add-button').forEach(button => {
        button.addEventListener('click', function() {
            const type = this.getAttribute('data-type');
            showAddForm(type);
        });
    });
    
    // 为搜索框添加事件监听器
    document.querySelectorAll('.search-input').forEach(input => {
        input.addEventListener('keyup', function(event) {
            if (event.key === 'Enter') {
                performSearch(this);
            }
        });
    });
    
    document.querySelectorAll('.search-button').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('.search-input');
            performSearch(input);
        });
    });
    
    // 为标签按钮添加事件监听器
    document.querySelectorAll('.tag-btn').forEach(button => {
        button.addEventListener('click', function() {
            // 更新活动标签按钮
            document.querySelectorAll('.tag-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            this.classList.add('active');
            
            // 获取选中的标签
            const selectedTagKey = this.getAttribute('data-tag');
            
            // 加载对应标签的数据
            if (selectedTagKey === 'all') {
                 loadItems('new-category'); // 这里我们简单地复用 loadItems 逻辑或者加载所有
            } else {
                 const tagId = TAG_MAP[selectedTagKey];
                 loadTaggedItems(tagId);
            }
        });
    });
    
    // 显示添加表单
    function showAddForm(type) {
        // 创建模态框
        const modal = document.createElement('div');
        modal.className = 'modal modal-overlay'; // 添加 class
        // 移除内联样式
        
        // 创建表单容器
        const formContainer = document.createElement('div');
        formContainer.className = 'modal-container'; // 添加 class
        // 移除内联样式
        
        // 表单标题
        const title = document.createElement('h2');
        title.textContent = type === 'books' ? '添加图书' : '添加电影';
        title.className = 'modal-title'; // 添加 class
        
        // 创建表单
        const form = document.createElement('form');
        form.className = 'add-item-form'; // 添加 class
        
        const formFields = type === 'books' ? 
        `
            <div class="form-group">
                <label>书名:</label>
                <input type="text" id="title" required>
            </div>
            <div class="form-group">
                <label>作者:</label>
                <input type="text" id="author" required>
            </div>
            <div class="form-group">
                <label>年份:</label>
                <input type="number" id="year" required>
            </div>
            <div class="form-group">
                <label>评分:</label>
                <input type="number" id="rating" min="0" max="10" step="0.1" required>
            </div>
            <div class="form-group">
                <label>封面链接 (可选):</label>
                <input type="text" id="cover">
            </div>
            <div class="form-group">
                <label>简介:</label>
                <textarea id="description" required></textarea>
            </div>
        ` :
        `
            <div class="form-group">
                <label>电影名:</label>
                <input type="text" id="title" required>
            </div>
            <div class="form-group">
                <label>导演:</label>
                <input type="text" id="director" required>
            </div>
            <div class="form-group">
                <label>年份:</label>
                <input type="number" id="year" required>
            </div>
            <div class="form-group">
                <label>评分:</label>
                <input type="number" id="rating" min="0" max="10" step="0.1" required>
            </div>
            <div class="form-group">
                <label>封面链接 (可选):</label>
                <input type="text" id="cover">
            </div>
            <div class="form-group">
                <label>简介:</label>
                <textarea id="description" required></textarea>
            </div>
        `;
        
        form.innerHTML = formFields;
        
        // 创建按钮容器
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'modal-buttons'; // 添加 class
        // 移除内联样式
        
        // 创建提交按钮
        const submitButton = document.createElement('button');
        submitButton.type = 'submit';
        submitButton.textContent = '添加';
        submitButton.className = 'btn-submit'; // 添加 class
        // 移除内联样式
        
        // 创建取消按钮
        const cancelButton = document.createElement('button');
        cancelButton.type = 'button';
        cancelButton.textContent = '取消';
        cancelButton.className = 'btn-cancel'; // 添加 class
        // 移除内联样式
        
        // 添加事件监听器
        cancelButton.addEventListener('click', function() {
            document.body.removeChild(modal);
        });
        
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const newItem = {
                title: document.getElementById('title').value,
                year: parseInt(document.getElementById('year').value),
                rating: parseFloat(document.getElementById('rating').value),
                description: document.getElementById('description').value
            };
            
            // 处理可选的封面链接
            const coverUrl = document.getElementById('cover').value;
            newItem.cover = coverUrl || 'https://via.placeholder.com/300x400.png?text=暂无封面';
            
            if (type === 'books') {
                newItem.author = document.getElementById('author').value;
            } else {
                newItem.director = document.getElementById('director').value;
            }
            
            // 发送请求到后端API
            fetch('/api/items', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({type, item: newItem})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('添加成功');
                    document.body.removeChild(modal);
                    // 重新加载数据
                    loadItems(type === 'books' ? 'book-catalog' : 'movie-catalog');
                } else {
                    alert('添加失败: ' + data.message);
                }
            })
            .catch(error => {
                console.error('添加失败:', error);
                alert('添加失败，请重试');
            });
        });
        
        // 组装模态框
        buttonContainer.appendChild(cancelButton);
        buttonContainer.appendChild(submitButton);
        form.appendChild(buttonContainer);
        formContainer.appendChild(title);
        formContainer.appendChild(form);
        modal.appendChild(formContainer);
        document.body.appendChild(modal);
    }
    
    // 执行搜索功能
    function performSearch(searchInput) {
        const searchTerm = searchInput.value.trim().toLowerCase();
        const dataType = searchInput.getAttribute('data-type');
        const sectionId = dataType === 'books' ? 'book-catalog' : 'movie-catalog';
        
        const container = document.getElementById(sectionId).querySelector('.items-grid');
        container.innerHTML = '';
        container.appendChild(loadingElement.cloneNode(true));

        // 调用 API 搜索
        let typeParam = dataType === 'books' ? 'book' : 'movie';
        fetch(`/api/public/items?type=${typeParam}&keyword=${encodeURIComponent(searchTerm)}`)
            .then(response => response.json())
            .then(result => {
                if (result.code === 200) {
                    displaySearchResults(result.data.records, sectionId, dataType);
                } else {
                    container.innerHTML = '<div class="error">搜索失败</div>';
                }
            })
            .catch(err => {
                console.error(err);
                container.innerHTML = '<div class="error">网络错误</div>';
            });
    }
    
    // 显示搜索结果
    function displaySearchResults(data, sectionId, dataType) {
        const container = document.getElementById(sectionId).querySelector('.items-grid');
        container.innerHTML = '';
        
        if (!data || data.length === 0) {
            container.innerHTML = '<div class="no-results">未找到匹配的结果</div>';
            return;
        }
        
        data.forEach(item => {
            const card = createItemCard(item, dataType);
            card.addEventListener('click', () => {
                // dataType 这里是 'books' 或 'movies'，后端 item.type 是 'book' 或 'movie'
                // detail 页面路由是 /detail/<item_type>/<item_id>，这里的 item_type 可以是 book/movie
                window.location.href = `/detail/${item.type}/${item.itemId}`;
            });
            container.appendChild(card);
        });
    }
    
    // 切换标签页
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabType = this.getAttribute('data-tab');
            
            // 更新按钮状态
            tabs.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            // 隐藏所有内容区域
            sections.forEach(section => section.classList.remove('active'));

            // 根据点击的标签页显示对应内容
            const targetSection = document.getElementById(tabType);
            if (targetSection) {
                targetSection.classList.add('active');
                
                // 对于图书目录和电影大全，每次都重新加载数据以确保显示最新的完整列表
                // 对于推荐类页面，只在没有内容时加载数据
                const itemsContainer = targetSection.querySelector('.items-grid');
                if (tabType === 'book-catalog' || tabType === 'movie-catalog' || tabType === 'new-category') {
                    // 显示加载状态并加载数据
                    itemsContainer.innerHTML = '';
                    itemsContainer.appendChild(loadingElement.cloneNode(true));
                    loadItems(tabType);
                } else if (itemsContainer.children.length === 0) {
                    // 对于其他标签页，只在没有内容时加载数据
                    itemsContainer.appendChild(loadingElement.cloneNode(true));
                    loadItems(tabType);
                }
            }
        });
    });
    
    // 初始加载图书推荐
    loadItems('books');
    
    // 加载推荐内容
    function loadItems(type) {
        let apiType = type;
        let queryParams = '';

        // 映射 type 到 API 参数
        if (type === 'book-catalog' || type === 'books') {
            queryParams = '?type=book';
            // 兼容前端逻辑，books 标签页可能需要特殊处理，这里暂且统一
        } else if (type === 'movie-catalog' || type === 'movies') {
            queryParams = '?type=movie';
        } else if (type === 'new-category') {
             // 默认加载所有，或者可以不传 type
             queryParams = '';
        }
        
        fetch(`/api/public/items${queryParams}`)
            .then(response => {
                if (response.status === 401) {
                    window.location.href = '/login';
                    return;
                }
                return response.json();
            })
            .then(result => {
                if (!result || result.code !== 200) return; 
                
                const data = result.data.records;
                const container = document.getElementById(`${type}`).querySelector('.items-grid');
                container.innerHTML = '';
                
                // 确定显示类型（用于创建卡片）
                // 虽然 createItemCard 的 type 参数不再严格需要 (因为 item 里有 type)，但保留兼容
                let displayType = type; 
                
                data.forEach(item => {
                    const card = createItemCard(item, displayType);
                    // 添加点击事件以查看详细信息
                    card.addEventListener('click', () => {
                        window.location.href = `/detail/${item.type}/${item.itemId}`;
                    });
                    container.appendChild(card);
                });
            })
            .catch(error => {
                console.error('加载失败:', error);
                const container = document.getElementById(`${type}`).querySelector('.items-grid');
                if (container) {
                    container.innerHTML = '<div class="error">加载失败，请刷新重试</div>';
                }
            });
    }
    
    // 加载带标签的项目
    function loadTaggedItems(tagId) {
        const container = document.getElementById('new-category').querySelector('.items-grid');
        container.innerHTML = '';
        container.appendChild(loadingElement.cloneNode(true));
        
        fetch(`/api/public/items?tagId=${tagId}`)
            .then(response => response.json())
            .then(result => {
                container.innerHTML = '';
                if (result.code === 200 && result.data.records.length > 0) {
                    result.data.records.forEach(item => {
                        const card = createItemCard(item, item.type + 's'); // 简单传递类型
                        card.addEventListener('click', () => {
                            window.location.href = `/detail/${item.type}/${item.itemId}`;
                        });
                        container.appendChild(card);
                    });
                } else {
                    container.innerHTML = '<div class="no-results">该标签下暂无内容</div>';
                }
            })
            .catch(error => {
                console.error(error);
                container.innerHTML = '<div class="error">加载失败</div>';
            });
    }
    
    // 创建卡片
    function createItemCard(item, type) {
        const card = document.createElement('div');
        card.className = 'item-card';
        
        // 适配后端字段
        const isBook = item.type === 'book';
        const typeLabel = isBook ? '作者' : '导演';
        const personName = item.authorDirector || '未知';
        
        card.innerHTML = `
            <div class="card-image-wrapper">
                <img src="${item.coverUrl}" alt="${item.title}" class="item-cover" onerror="this.onerror=null;this.src='https://via.placeholder.com/300x400.png?text=封面图片';">
                <div class="card-overlay">
                    <span class="view-btn">查看详情</span>
                </div>
            </div>
            <div class="item-info">
                <h3 class="item-title">${item.title}</h3>
                <p class="item-author">${typeLabel}: ${personName}</p>
                <div class="item-meta">
                    <span class="item-year">${item.releaseYear}</span>
                    <div class="item-rating">
                        <span class="rating-star">★</span>
                        <span class="rating-score">${item.ratingAvg}</span>
                    </div>
                </div>
            </div>
        `;
        return card;
    }
});
