import React, { useState } from 'react';
import { Avatar, Card, CardContent, CardHeader, Typography, IconButton, Box, Chip, Divider } from '@mui/material';
import { Favorite, FavoriteBorder, Comment } from '@mui/icons-material';
import { Post } from '../types';
import { postsAPI } from '../services/api';
import { format } from 'date-fns';
import { he } from 'date-fns/locale';

interface PostCardProps {
  post: Post;
  onLikeToggle?: (postId: number, isLiked: boolean) => void;
}

const PostCard: React.FC<PostCardProps> = ({ post, onLikeToggle }) => {
  const [isLiked, setIsLiked] = useState(post.is_liked);
  const [likesCount, setLikesCount] = useState(post.likes_count);
  
  const handleLike = async () => {
    try {
      if (isLiked) {
        await postsAPI.unlikePost(post.id);
        setIsLiked(false);
        setLikesCount(prev => prev - 1);
      } else {
        await postsAPI.likePost(post.id);
        setIsLiked(true);
        setLikesCount(prev => prev + 1);
      }
      // Call parent handler if provided
      if (onLikeToggle) {
        onLikeToggle(post.id, !isLiked);
      }
    } catch (error) {
      console.error('Error toggling like:', error);
    }
  };
  
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return format(date, "d בMMM yyyy, HH:mm", { locale: he });
    } catch (e) {
      return dateString;
    }
  };
  
  return (
    <Card sx={{ mb: 2, borderRadius: 2 }}>
      <CardHeader
        avatar={
          <Avatar sx={{ bgcolor: 'primary.main' }}>
            {post.author.username.charAt(0).toUpperCase()}
          </Avatar>
        }
        title={post.author.full_name || post.author.username}
        subheader={`@${post.author.username}`}
        action={
          post.programming_language && (
            <Chip 
              label={post.programming_language.name} 
              size="small" 
              color="primary" 
              variant="outlined"
              sx={{ mr: 2, mt: 1 }}
            />
          )
        }
      />
      <CardContent>
        <Typography variant="body1" component="p" sx={{ whiteSpace: 'pre-wrap', mb: 2 }}>
          {post.content}
        </Typography>
        
        {post.code_snippet && (
          <Box
            sx={{
              bgcolor: 'grey.900',
              color: 'grey.100',
              p: 2,
              borderRadius: 1,
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              overflow: 'auto',
              mb: 2,
              whiteSpace: 'pre-wrap',
            }}
          >
            {post.code_snippet}
          </Box>
        )}
        
        <Divider sx={{ my: 1 }} />
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton 
              size="small" 
              onClick={handleLike}
              color={isLiked ? 'error' : 'default'}
            >
              {isLiked ? <Favorite /> : <FavoriteBorder />}
            </IconButton>
            <Typography variant="body2" color="text.secondary" sx={{ mr: 2 }}>
              {likesCount}
            </Typography>
            
            <IconButton size="small">
              <Comment />
            </IconButton>
            <Typography variant="body2" color="text.secondary">
              {post.comments_count}
            </Typography>
          </Box>
          
          <Typography variant="caption" color="text.secondary">
            {formatDate(post.created_at)}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default PostCard; 