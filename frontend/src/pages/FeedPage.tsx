import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Grid, 
  Typography, 
  Box, 
  Paper, 
  CircularProgress, 
  Button,
  Divider,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { postsAPI, programmingLanguagesAPI } from '../services/api';
import { Post, ProgrammingLanguage } from '../types';
import PostCard from '../components/PostCard';
import CreatePostForm from '../components/CreatePostForm';

const FeedPage: React.FC = () => {
  const { user } = useAuth();
  const [posts, setPosts] = useState<Post[]>([]);
  const [languages, setLanguages] = useState<ProgrammingLanguage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const fetchPosts = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await postsAPI.getPosts();
      setPosts(response.results);
    } catch (error) {
      console.error('Error fetching posts:', error);
      setError('אירעה שגיאה בטעינת הפוסטים. אנא נסה שוב מאוחר יותר.');
    } finally {
      setIsLoading(false);
    }
  };
  
  const fetchLanguages = async () => {
    try {
      const data = await programmingLanguagesAPI.getLanguages();
      setLanguages(data);
    } catch (error) {
      console.error('Error fetching programming languages:', error);
    }
  };
  
  useEffect(() => {
    fetchPosts();
    fetchLanguages();
  }, []);
  
  const handlePostCreated = () => {
    fetchPosts();
  };
  
  const handleLikeToggle = (postId: number, isLiked: boolean) => {
    // Update local state to reflect the like change
    setPosts(prevPosts => 
      prevPosts.map(post => 
        post.id === postId 
          ? { 
              ...post, 
              is_liked: isLiked, 
              likes_count: isLiked ? post.likes_count + 1 : post.likes_count - 1 
            } 
          : post
      )
    );
  };
  
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Left Sidebar - User Profile */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            {user && (
              <Box sx={{ textAlign: 'center', mb: 2 }}>
                <Avatar 
                  sx={{ width: 80, height: 80, mx: 'auto', mb: 2, bgcolor: 'primary.main' }}
                >
                  {user.username.charAt(0).toUpperCase()}
                </Avatar>
                <Typography variant="h6">{user.full_name || user.username}</Typography>
                <Typography variant="body2" color="text.secondary">@{user.username}</Typography>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-around', mt: 2 }}>
                  <Box>
                    <Typography variant="h6">{user.following_count}</Typography>
                    <Typography variant="body2" color="text.secondary">עוקב</Typography>
                  </Box>
                  <Box>
                    <Typography variant="h6">{user.followers_count}</Typography>
                    <Typography variant="body2" color="text.secondary">עוקבים</Typography>
                  </Box>
                </Box>
                
                {user.bio && (
                  <Typography variant="body2" sx={{ mt: 2, textAlign: 'right' }}>
                    {user.bio}
                  </Typography>
                )}
              </Box>
            )}
          </Paper>
          
          {/* Programming Languages */}
          <Paper sx={{ p: 2, mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              שפות תכנות
            </Typography>
            <List dense>
              {languages.map(language => (
                <ListItem key={language.id}>
                  <ListItemText primary={language.name} />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
        
        {/* Main Feed */}
        <Grid item xs={12} md={6}>
          <CreatePostForm onPostCreated={handlePostCreated} />
          
          {isLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography color="error">{error}</Typography>
              <Button 
                variant="outlined" 
                color="primary" 
                onClick={fetchPosts}
                sx={{ mt: 2 }}
              >
                נסה שוב
              </Button>
            </Paper>
          ) : posts.length === 0 ? (
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography>אין פוסטים להצגה</Typography>
            </Paper>
          ) : (
            posts.map(post => (
              <PostCard 
                key={post.id} 
                post={post} 
                onLikeToggle={handleLikeToggle}
              />
            ))
          )}
        </Grid>
        
        {/* Right Sidebar - Suggestions */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              הצעות לעקוב
            </Typography>
            <Typography variant="body2" color="text.secondary">
              יוצג בקרוב...
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default FeedPage; 