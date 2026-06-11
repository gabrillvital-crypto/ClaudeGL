import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import fs from 'fs'

// Plugin to serve CSV data files from the existing Dashboard/data directory
const dataServerPlugin = () => ({
  name: 'serve-dashboard-data',
  configureServer(server: any) {
    const dataDir = path.resolve(__dirname, 'data')
    server.middlewares.use('/data', (req: any, res: any, next: any) => {
      const filePath = path.join(dataDir, req.url as string)
      if (!fs.existsSync(filePath)) { next(); return }
      const content = fs.readFileSync(filePath)
      res.setHeader('Content-Type', 'text/csv; charset=utf-8')
      res.setHeader('Access-Control-Allow-Origin', '*')
      res.end(content)
    })
  }
})

export default defineConfig({
  plugins: [react(), dataServerPlugin()],
  server: {
    port: 5173,
    open: true
  }
})
