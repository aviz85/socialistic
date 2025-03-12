import React, { useState, useEffect } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  Paper,
  Typography,
  CircularProgress,
  Alert
} from '@mui/material';
import { ProgrammingLanguage } from '../types';
import { postsAPI, programmingLanguagesAPI } from '../services/api';

interface CreatePostFormProps {
  onPostCreated: () => void;
}

const CreatePostForm: React.FC<CreatePostFormProps> = ({ onPostCreated }) => {
  const [content, setContent] = useState('');
  const [codeSnippet, setCodeSnippet] = useState<string | null>('');
  const [programmingLanguageId, setProgrammingLanguageId] = useState<number | ''>('');
  const [languages, setLanguages] = useState<ProgrammingLanguage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchLanguages = async () => {
      try {
        const data = await programmingLanguagesAPI.getLanguages();
        setLanguages(data);
      } catch (error) {
        console.error('Error fetching programming languages:', error);
      }
    };
    
    fetchLanguages();
  }, []);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!content.trim()) {
      setError('תוכן הפוסט לא יכול להיות ריק');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const postData = {
        content,
        code_snippet: codeSnippet && codeSnippet.trim() ? codeSnippet : null,
        programming_language_id: programmingLanguageId !== '' ? Number(programmingLanguageId) : undefined
      };
      
      await postsAPI.createPost(postData);
      
      // Reset form
      setContent('');
      setCodeSnippet('');
      setProgrammingLanguageId('');
      
      // Notify parent component
      onPostCreated();
    } catch (error) {
      console.error('Error creating post:', error);
      setError('אירעה שגיאה ביצירת הפוסט. אנא נסה שוב מאוחר יותר.');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" component="h2" gutterBottom>
        יצירת פוסט חדש
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Box component="form" onSubmit={handleSubmit} noValidate>
        <TextField
          fullWidth
          multiline
          rows={3}
          label="תוכן הפוסט"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          margin="normal"
          required
          inputProps={{ dir: 'auto' }}
        />
        
        <TextField
          fullWidth
          multiline
          rows={4}
          label="קטע קוד (אופציונלי)"
          value={codeSnippet || ''}
          onChange={(e) => setCodeSnippet(e.target.value)}
          margin="normal"
          inputProps={{ 
            style: { fontFamily: 'monospace' },
            dir: 'ltr'
          }}
        />
        
        <FormControl fullWidth margin="normal">
          <InputLabel id="programming-language-label">שפת תכנות (אופציונלי)</InputLabel>
          <Select
            labelId="programming-language-label"
            value={programmingLanguageId}
            onChange={(e) => setProgrammingLanguageId(e.target.value as number | '')}
            label="שפת תכנות (אופציונלי)"
          >
            <MenuItem value="">
              <em>ללא</em>
            </MenuItem>
            {languages.map((language) => (
              <MenuItem key={language.id} value={language.id}>
                {language.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
        
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={isLoading || !content.trim()}
          >
            {isLoading ? <CircularProgress size={24} /> : 'פרסם'}
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};

export default CreatePostForm; 