module.exports = {
  apps: [
    {
      name: "campaignmaker-backend",
      cwd: "./backend",
      script: ".venv/bin/uvicorn",
      args: "app.main:app --host 0.0.0.0 --port 24000",
      interpreter: "none",
      env: {
        NODE_ENV: "production",
      }
    },
    {
      name: "campaignmaker-frontend",
      cwd: "./frontend",
      script: "npm",
      args: "start",
      env: {
        NODE_ENV: "production",
        PORT: 14000
      }
    }
  ]
}
