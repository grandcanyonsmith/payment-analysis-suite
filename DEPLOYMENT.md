# Deployment Guide for Vercel

## Quick Deploy to Vercel

Your presentation is now ready to be deployed on Vercel! Follow these steps:

### Option 1: Deploy with Vercel CLI

1. Install Vercel CLI (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. From the project root directory, run:
   ```bash
   vercel
   ```

3. Follow the prompts:
   - Confirm the project setup
   - Choose a project name
   - The presentation will be automatically deployed

### Option 2: Deploy via GitHub

1. Push this project to a GitHub repository
2. Go to [vercel.com](https://vercel.com)
3. Click "New Project"
4. Import your GitHub repository
5. Vercel will automatically detect the configuration and deploy

### Option 3: Direct Upload

1. Go to [vercel.com](https://vercel.com)
2. Drag and drop the entire project folder
3. Vercel will handle the rest

## What's Configured

- **vercel.json**: Configures Vercel to serve the `presentation` directory
- **package.json**: Defines the project for Vercel
- **presentation/index.html**: Your presentation slides

## After Deployment

Once deployed, you'll get a URL like:
- `https://your-project-name.vercel.app`

When you open this URL, you'll immediately see your presentation starting from the first slide.

## Local Development

To preview locally before deploying:
```bash
python -m http.server 8000 --directory presentation
```
Then open http://localhost:8000 in your browser.

## Slide Navigation

The presentation includes 8 slides that show:
1. Title and critical alert
2. Executive summary with key metrics
3. Core problem analysis
4. Financial impact breakdown
5. Root cause analysis
6. Immediate action plan
7. Implementation roadmap
8. Expected results

Use arrow keys or click to navigate between slides (if you want to add this functionality).