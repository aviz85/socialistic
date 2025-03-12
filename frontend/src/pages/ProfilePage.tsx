import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Grid, 
  Typography, 
  Box, 
  Paper, 
  Button, 
  Avatar, 
  Tabs, 
  Tab, 
  CircularProgress,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  TextField
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { usersAPI, postsAPI } from '../services/api';
import { User, Post, Skill } from '../types';
import PostCard from '../components/PostCard';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`profile-tabpanel-${index}`}
      aria-labelledby={`profile-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

const ProfilePage: React.FC = () => {
  const { username } = useParams<{ username: string }>();
  const { user: currentUser, updateUser } = useAuth();
  const navigate = useNavigate();
  
  const [profileUser, setProfileUser] = useState<User | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    fullName: '',
    bio: ''
  });
  
  const isOwnProfile = currentUser?.username === username;
  
  useEffect(() => {
    const fetchProfileData = async () => {
      setIsLoading(true);
      setError(null);
      
      try {
        // If viewing own profile and we already have the data
        if (isOwnProfile && currentUser) {
          setProfileUser(currentUser);
          setEditForm({
            fullName: currentUser.full_name || '',
            bio: currentUser.bio || ''
          });
        } else if (username) {
          // Fetch user profile
          const userData = await usersAPI.getUserProfile(username);
          setProfileUser(userData);
          
          if (isOwnProfile) {
            setEditForm({
              fullName: userData.full_name || '',
              bio: userData.bio || ''
            });
          }
        }
        
        // Fetch user posts
        if (username) {
          const postsData = await postsAPI.getUserPosts(username);
          setPosts(postsData.results);
        }
      } catch (error) {
        console.error('Error fetching profile data:', error);
        setError('אירעה שגיאה בטעינת הפרופיל. אנא נסה שוב מאוחר יותר.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchProfileData();
  }, [username, currentUser, isOwnProfile]);
  
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };
  
  const handleEditProfile = () => {
    setIsEditing(true);
  };
  
  const handleCancelEdit = () => {
    if (profileUser) {
      setEditForm({
        fullName: profileUser.full_name || '',
        bio: profileUser.bio || ''
      });
    }
    setIsEditing(false);
  };
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setEditForm(prev => ({ ...prev, [name]: value }));
  };
  
  const handleSaveProfile = async () => {
    if (!currentUser) return;
    
    try {
      const updatedUser = await usersAPI.updateProfile({
        full_name: editForm.fullName,
        bio: editForm.bio
      });
      
      setProfileUser(updatedUser);
      updateUser(updatedUser);
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating profile:', error);
      setError('אירעה שגיאה בעדכון הפרופיל. אנא נסה שוב.');
    }
  };
  
  const handleFollowToggle = async () => {
    if (!profileUser || !currentUser) return;
    
    try {
      if (profileUser.is_followed) {
        await usersAPI.unfollowUser(profileUser.username);
        setProfileUser({
          ...profileUser,
          is_followed: false,
          followers_count: profileUser.followers_count - 1
        });
      } else {
        await usersAPI.followUser(profileUser.username);
        setProfileUser({
          ...profileUser,
          is_followed: true,
          followers_count: profileUser.followers_count + 1
        });
      }
    } catch (error) {
      console.error('Error toggling follow:', error);
    }
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
  
  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }
  
  if (error || !profileUser) {
    return (
      <Container maxWidth="md">
        <Paper sx={{ p: 3, textAlign: 'center', mt: 4 }}>
          <Typography color="error">{error || 'משתמש לא נמצא'}</Typography>
          <Button 
            variant="outlined" 
            color="primary" 
            onClick={() => navigate('/feed')}
            sx={{ mt: 2 }}
          >
            חזור לדף הראשי
          </Button>
        </Paper>
      </Container>
    );
  }
  
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={3}>
          {/* Profile Header */}
          <Grid item xs={12} md={3} sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Avatar 
              sx={{ width: 120, height: 120, mb: 2, bgcolor: 'primary.main' }}
            >
              {profileUser.username.charAt(0).toUpperCase()}
            </Avatar>
            
            {!isEditing && isOwnProfile && (
              <Button 
                variant="outlined" 
                color="primary" 
                onClick={handleEditProfile}
                sx={{ mb: 2, width: '100%' }}
              >
                ערוך פרופיל
              </Button>
            )}
            
            {!isOwnProfile && (
              <Button 
                variant={profileUser.is_followed ? "outlined" : "contained"} 
                color="primary" 
                onClick={handleFollowToggle}
                sx={{ mb: 2, width: '100%' }}
              >
                {profileUser.is_followed ? 'הפסק לעקוב' : 'עקוב'}
              </Button>
            )}
          </Grid>
          
          <Grid item xs={12} md={9}>
            {isEditing ? (
              <Box component="form">
                <TextField
                  fullWidth
                  label="שם מלא"
                  name="fullName"
                  value={editForm.fullName}
                  onChange={handleInputChange}
                  margin="normal"
                />
                <TextField
                  fullWidth
                  label="ביוגרפיה"
                  name="bio"
                  value={editForm.bio}
                  onChange={handleInputChange}
                  multiline
                  rows={3}
                  margin="normal"
                />
                <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                  <Button variant="contained" color="primary" onClick={handleSaveProfile}>
                    שמור
                  </Button>
                  <Button variant="outlined" onClick={handleCancelEdit}>
                    בטל
                  </Button>
                </Box>
              </Box>
            ) : (
              <>
                <Typography variant="h4" gutterBottom>
                  {profileUser.full_name || profileUser.username}
                </Typography>
                <Typography variant="body1" color="text.secondary" gutterBottom>
                  @{profileUser.username}
                </Typography>
                
                {profileUser.bio && (
                  <Typography variant="body1" paragraph sx={{ mt: 2 }}>
                    {profileUser.bio}
                  </Typography>
                )}
                
                <Box sx={{ display: 'flex', gap: 4, mt: 2 }}>
                  <Box>
                    <Typography variant="h6">{profileUser.posts_count}</Typography>
                    <Typography variant="body2" color="text.secondary">פוסטים</Typography>
                  </Box>
                  <Box>
                    <Typography variant="h6">{profileUser.followers_count}</Typography>
                    <Typography variant="body2" color="text.secondary">עוקבים</Typography>
                  </Box>
                  <Box>
                    <Typography variant="h6">{profileUser.following_count}</Typography>
                    <Typography variant="body2" color="text.secondary">עוקב</Typography>
                  </Box>
                </Box>
              </>
            )}
          </Grid>
        </Grid>
      </Paper>
      
      {/* Tabs */}
      <Box sx={{ width: '100%' }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} centered>
            <Tab label="פוסטים" />
            <Tab label="מיומנויות" />
          </Tabs>
        </Box>
        
        <TabPanel value={tabValue} index={0}>
          {posts.length === 0 ? (
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
        </TabPanel>
        
        <TabPanel value={tabValue} index={1}>
          {profileUser.skills && profileUser.skills.length > 0 ? (
            <List>
              {profileUser.skills.map((skill: Skill) => (
                <ListItem key={skill.id}>
                  <ListItemText primary={skill.name} />
                </ListItem>
              ))}
            </List>
          ) : (
            <Paper sx={{ p: 3, textAlign: 'center' }}>
              <Typography>אין מיומנויות להצגה</Typography>
            </Paper>
          )}
        </TabPanel>
      </Box>
    </Container>
  );
};

export default ProfilePage; 