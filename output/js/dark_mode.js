const toggle = document.getElementById('theme-toggle')

if (localStorage.getItem('theme') === 'dark' || (!localStorage.getItem('theme') && window.watchMedia('(prefers-color-scheme: dark)').matches)) {
  document.documentElement.setAttribute('data-theme', 'dark')
}

toggle.addEventListener('click', () => {
   if (document.documentElement.getAttribute('data-theme') === 'dark') {
      document.documentElement.setAttribute('data-theme', 'light');
      localStorage.setItem('theme', 'light');
    } else {
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('theme', 'dark');
    }
})