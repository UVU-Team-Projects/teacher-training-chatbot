# Example Bug Report

This is an example of a well-written bug report. Notice how it provides clear information and helps developers understand and reproduce the issue.

```markdown
# Bug Report: AI Model Response Times Exceed 5 Seconds on Large Inputs

## Bug Description
The AI model (Llama-2-7b) is taking more than 5 seconds to respond when the input text is longer than 200 words. This is causing the UI to appear unresponsive and affecting the user experience. Our performance requirement is to have responses within 2 seconds.

## Steps to Reproduce
1. Go to the chat interface at '/chat'
2. Paste the following long text (attached below) into the input field
3. Click 'Submit' or press Enter
4. Watch the loading spinner

Test Input:
```text
[Long text example that triggers the issue - 250 words]
```

## Expected Behavior
- Response should be generated within 2 seconds
- Loading spinner should not appear for more than 2 seconds
- UI should remain responsive during processing

## Actual Behavior
- Response takes 5-7 seconds to generate
- Loading spinner appears for the entire duration
- UI becomes unresponsive during processing
- Console shows performance warnings

## Screenshots
### Performance Timeline
![Performance Timeline](https://example.com/performance-timeline.png)

### Console Warnings
![Console Warnings](https://example.com/console-warnings.png)

## Environment
- OS: macOS 12.0
- Browser: Chrome 96
- Python Version: 3.9.7
- Model Version: Llama-2-7b-chat.Q4_K_M.gguf
- Other relevant dependencies:
  ```
  llama-cpp-python==0.2.0
  sentence-transformers==2.2.2
  ```

## Console Output
```
WARNING: Response generation exceeded timeout threshold
Time taken: 5234ms
Memory usage: 1.2GB
GPU utilization: 95%
```

## Additional Context
- Issue occurs more frequently during peak usage hours
- Problem started after the last model update
- Only affects inputs longer than 200 words
- Memory usage spikes during processing

## Possible Solution
Potential fixes to investigate:
1. Implement request batching
2. Add input text chunking
3. Optimize model quantization
4. Enable GPU acceleration

## Related Issues
- Related to #234 (Performance Optimization Epic)
- Similar to #156 (Previous Timeout Issues)

## Impact
- [x] High (Breaking functionality)
- [ ] Medium (Major inconvenience)
- [ ] Low (Minor inconvenience)

## Component
- [ ] Database
- [x] AI Model
- [ ] Frontend
- [ ] API
- [ ] Documentation

## Checklist
- [x] I have checked for similar issues
- [x] I have included all relevant information
- [x] I have added appropriate labels
- [x] I have tested with the latest version
```

## Why This is a Good Example

### 1. Clear Problem Description
- Specific issue identified
- Performance metrics included
- Impact clearly stated

### 2. Detailed Reproduction Steps
- Step-by-step instructions
- Test input provided
- Environment details included

### 3. Evidence Provided
- Screenshots included
- Console output shared
- Performance metrics shown

### 4. Context and Impact
- Related issues linked
- Impact level specified
- Component identified

### 5. Helpful Additional Information
- Possible solutions suggested
- Patterns identified
- System state described

## Common Mistakes This Example Avoids

1. ❌ Vague problem description
2. ❌ Missing reproduction steps
3. ❌ No error messages
4. ❌ Incomplete environment info
5. ❌ No context or patterns

## How to Use This Example

1. Follow the same structure
2. Include specific details
3. Provide clear steps
4. Add relevant logs/screenshots
5. Suggest possible solutions
6. Link related issues

## Tips for Writing Bug Reports

1. **Be Specific**
   - Include exact error messages
   - Provide specific numbers
   - Describe exact behavior

2. **Be Complete**
   - Include all relevant info
   - Describe the environment
   - Show reproduction steps

3. **Be Helpful**
   - Suggest possible causes
   - Include workarounds if known
   - Provide context
``` 