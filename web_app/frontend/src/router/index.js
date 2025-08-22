import { createRouter, createWebHistory } from 'vue-router'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: {
      title: '上传分析 - Kindle知识图谱',
      description: '上传Kindle HTML文件，生成智能知识图谱'
    }
  },
  {
    path: '/upload',
    name: 'Upload', 
    component: () => import('../views/Upload.vue'),
    meta: {
      title: '文件上传 - Kindle知识图谱'
    }
  },
  {
    path: '/tasks',
    name: 'Tasks',
    component: () => import('../views/Tasks.vue'),
    meta: {
      title: '任务历史 - Kindle知识图谱',
      description: '查看所有分析任务的历史记录'
    }
  },
  {
    path: '/task/:id',
    name: 'TaskDetail',
    component: () => import('../views/TaskDetail.vue'),
    meta: {
      title: '任务详情 - Kindle知识图谱'
    },
    props: true
  },
  {
    path: '/graph/:id',
    name: 'GraphView',
    component: () => import('../views/GraphView.vue'),
    meta: {
      title: '知识图谱 - Kindle知识图谱',
      description: '交互式知识网络可视化'
    },
    props: true
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue'),
    meta: {
      title: '关于 - Kindle知识图谱'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: {
      title: '页面未找到 - Kindle知识图谱'
    }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // 路由切换时的滚动行为
    if (savedPosition) {
      return savedPosition
    } else if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth'
      }
    } else {
      return { top: 0 }
    }
  }
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  // 更新页面标题
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  // 更新meta描述
  if (to.meta.description) {
    const metaDescription = document.querySelector('meta[name="description"]')
    if (metaDescription) {
      metaDescription.setAttribute('content', to.meta.description)
    }
  }
  
  next()
})

router.afterEach((to, from) => {
  // 路由切换后的处理，如analytics等
  console.log(`Navigation: ${from.path} → ${to.path}`)
})

export default router