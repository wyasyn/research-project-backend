```bash
conda create -n myenv python=3.12
conda activate myenv
conda install dlib
conda install -c conda-forge face_recognition
```

## Example fetch with token

```js
fetch("http://localhost:5000/protected-endpoint", {
  method: "GET",
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```
