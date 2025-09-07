<script setup lang="ts">
import { RouterView, RouterLink } from 'vue-router'
</script>

<template>
  <div class="app-layout">
    <aside class="sidebar">
    </aside>

    <section class="main-area">
      <header class="top-nav">
        <!-- top nav for switching routes as requested -->
        <nav>
          <ul>
            <li>
              <RouterLink to="/">全文搜索</RouterLink>
            </li>
            <li>
              <RouterLink to="/semantic">语义搜索</RouterLink>
            </li>
            <li>
              <RouterLink to="/llm">LLM问答</RouterLink>
            </li>
          </ul>
        </nav>
      </header>

      <main class="content">
        <!-- nested routes render here -->
        <RouterView />
      </main>
    </section>
  </div>
</template>

<style>
body {
  margin: 0;
}

/* Layout for App: left sidebar, top navigation in main area, and scrollable main content */
.app-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  /* sidebar + main */
  grid-template-rows: 1fr;
  gap: 1rem;
  height: 100vh;
  /* full viewport so content can scroll internally */
}

.sidebar {
  background: rgba(0, 0, 0, 0.03);
  padding: 1rem;
  border-right: 1px solid rgba(0, 0, 0, 0.06);
  overflow: auto;
  /* allow sidebar to scroll if content grows */
}

.main-area {
  display: flex;
  flex-direction: column;
  min-height: 0;
  /* allow children with overflow to behave correctly */
}

.top-nav {
  background: transparent;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  padding: 0.5rem 1rem;
  flex: 0 0 auto;
}

.top-nav nav ul {
  display: flex;
  gap: 1rem;
  margin: 0;
  padding: 0;
  list-style: none;
  align-items: center;
}

.content {
  padding: 1rem;
  overflow: auto;
  /* scroll content inside main-area */
  flex: 1 1 0%;
  min-height: 0;
  /* required for correct scrolling in flex containers */
}

/* Responsive: stack sidebar above main on small screens */
@media (max-width: 768px) {
  .app-layout {
    grid-template-columns: 1fr;
    grid-auto-rows: auto 1fr;
    height: auto;
  }

  .sidebar {
    border-right: none;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    width: 100%;
  }

  .top-nav nav ul {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
}
</style>
