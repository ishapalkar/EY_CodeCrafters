import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Button } from './components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import Chat from './components/Chat';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </div>
    </Router>
  );
}

function HomePage() {
  return (
    <div className="container mx-auto p-6">
      <div className="flex flex-col items-center justify-center min-h-screen gap-8">
        <h1 className="text-6xl font-bold font-heading bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent animate-text-shimmer">
          Welcome to Code Crafters
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl text-center">
          Your React + Tailwind CSS project is ready! Start building amazing things.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12 w-full max-w-6xl">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle>🚀 Fast Setup</CardTitle>
              <CardDescription>
                React 19 + Vite for lightning-fast development
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm">
                Hot module replacement and instant feedback for rapid iteration.
              </p>
            </CardContent>
          </Card>
          
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle>🎨 Tailwind CSS</CardTitle>
              <CardDescription>
                Utility-first CSS framework with custom configuration
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm">
                Dark mode support, custom animations, and beautiful design tokens.
              </p>
            </CardContent>
          </Card>
          
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle>📦 UI Components</CardTitle>
              <CardDescription>
                Radix UI primitives with shadcn/ui styling
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm">
                Accessible, customizable components ready to use.
              </p>
            </CardContent>
          </Card>
        </div>
        
        <div className="flex gap-4 mt-8">
          <Link to="/chat">
            <Button size="lg" className="animate-button-hover">
              Open AI Sales Chat
            </Button>
          </Link>
          <Button size="lg" variant="outline">
            Learn More
          </Button>
        </div>
      </div>
    </div>
  );
}

export default App;
