# 📱 Mobile Developer Quick Start Guide

## For iOS Developers (Swift/SwiftUI)

### 1. API Configuration

```swift
import Foundation

class APIClient {
    static let shared = APIClient()
    let baseURL = "http://your-server.com"  // Change to your API
    var authToken: String?
    
    func register(username: String, password: String, fullName: String) async throws {
        let payload = [
            "username": username,
            "password": password,
            "full_name": fullName,
            "role": "mechanic"
        ]
        
        let request = createRequest(
            endpoint: "/users/register",
            method: "POST",
            body: payload
        )
        
        let (data, response) = try await URLSession.shared.data(for: request)
        try handleResponse(response)
        print("User registered successfully!")
    }
    
    func login(username: String, password: String) async throws {
        var request = URLRequest(url: URL(string: "\(baseURL)/users/token")!)
        request.httpMethod = "POST"
        
        let bodyString = "username=\(username)&password=\(password)"
        request.httpBody = bodyString.data(using: .utf8)
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        try handleResponse(response)
        
        let result = try JSONDecoder().decode(TokenResponse.self, from: data)
        self.authToken = result.access_token
        UserDefaults.standard.set(authToken, forKey: "auth_token")
    }
    
    func fetchInventory() async throws -> [InventoryItem] {
        let request = createRequest(
            endpoint: "/inventory/",
            method: "GET",
            authenticated: true
        )
        
        let (data, response) = try await URLSession.shared.data(for: request)
        try handleResponse(response)
        return try JSONDecoder().decode([InventoryItem].self, from: data)
    }
    
    private func createRequest(endpoint: String, method: String, body: Any? = nil, authenticated: Bool = false) -> URLRequest {
        var request = URLRequest(url: URL(string: "\(baseURL)\(endpoint)")!)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if authenticated, let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        if let body = body {
            request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        }
        
        return request
    }
    
    private func handleResponse(_ response: URLResponse) throws {
        guard let httpResponse = response as? HTTPURLResponse else { return }
        
        switch httpResponse.statusCode {
        case 200...299:
            break
        case 401:
            throw APIError.unauthorized
        case 404:
            throw APIError.notFound
        case 422:
            throw APIError.validationError
        default:
            throw APIError.serverError
        }
    }
}

// Data Models
struct TokenResponse: Codable {
    let access_token: String
    let token_type: String
}

struct InventoryItem: Codable {
    let id: Int
    let part_number: String
    let name: String
    let category: String
    let stock_level: Int
    let price: Double
}

enum APIError: Error {
    case unauthorized
    case notFound
    case validationError
    case serverError
}
```

### 2. SwiftUI View Example

```swift
import SwiftUI

struct LoginView: View {
    @State private var username = ""
    @State private var password = ""
    @State private var isLoading = false
    @State private var errorMessage = ""
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Engineering App")
                .font(.title)
                .bold()
            
            TextField("Username", text: $username)
                .textFieldStyle(.roundedBorder)
                .autocapitalization(.none)
            
            SecureField("Password", text: $password)
                .textFieldStyle(.roundedBorder)
            
            if !errorMessage.isEmpty {
                Text(errorMessage)
                    .foregroundColor(.red)
                    .font(.caption)
            }
            
            Button(action: login) {
                if isLoading {
                    ProgressView()
                        .progressViewStyle(.circular)
                } else {
                    Text("Login")
                }
            }
            .disabled(isLoading)
            .frame(maxWidth: .infinity)
            .padding()
            .background(Color.blue)
            .foregroundColor(.white)
            .cornerRadius(8)
        }
        .padding()
    }
    
    func login() {
        isLoading = true
        Task {
            do {
                try await APIClient.shared.login(username: username, password: password)
                // Navigate to next screen
            } catch {
                errorMessage = error.localizedDescription
            }
            isLoading = false
        }
    }
}
```

---

## For Android Developers (Kotlin/Jetpack Compose)

### 1. Retrofit API Configuration

```kotlin
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import okhttp3.OkHttpClient
import okhttp3.Interceptor
import com.google.gson.annotations.SerializedName

interface EngineeringAPI {
    @POST("/users/register")
    suspend fun registerUser(@Body request: RegisterRequest): UserResponse
    
    @POST("/users/token")
    @FormUrlEncoded
    suspend fun login(
        @Field("username") username: String,
        @Field("password") password: String
    ): TokenResponse
    
    @GET("/inventory/")
    suspend fun getInventory(
        @Query("skip") skip: Int = 0,
        @Query("limit") limit: Int = 100
    ): List<InventoryItem>
    
    @POST("/job-cards/")
    suspend fun createJobCard(@Body request: JobCardRequest): JobCardResponse
}

// Data Classes
data class RegisterRequest(
    val username: String,
    val password: String,
    val full_name: String,
    val role: String = "mechanic"
)

data class UserResponse(
    val id: Int,
    val username: String,
    val full_name: String,
    val role: String
)

data class TokenResponse(
    val access_token: String,
    val token_type: String
)

data class InventoryItem(
    val id: Int,
    val part_number: String,
    val name: String,
    val category: String,
    val stock_level: Int,
    val price: Double
)

data class JobCardRequest(
    val mechanic_id: Int,
    val machine_id: Int,
    val problem_description: String
)

data class JobCardResponse(
    val id: Int,
    val status: String,
    val created_at: String
)

// Retrofit Instance
object RetrofitClient {
    private var authToken: String? = null
    
    val apiService: EngineeringAPI by lazy {
        val client = OkHttpClient.Builder()
            .addInterceptor(AuthInterceptor())
            .build()
        
        Retrofit.Builder()
            .baseUrl("http://your-server.com/")  // Change to your API
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(EngineeringAPI::class.java)
    }
    
    fun setAuthToken(token: String) {
        authToken = token
    }
    
    private class AuthInterceptor : Interceptor {
        override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
            val request = chain.request().newBuilder()
                .apply {
                    authToken?.let {
                        addHeader("Authorization", "Bearer $it")
                    }
                    addHeader("Content-Type", "application/json")
                }
                .build()
            return chain.proceed(request)
        }
    }
}
```

### 2. Jetpack Compose Example

```kotlin
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.lifecycle.viewmodel.compose.viewModel

@Composable
fun LoginScreen(viewModel: AuthViewModel = viewModel()) {
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    val state by viewModel.state.collectAsState()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            "Engineering App",
            style = MaterialTheme.typography.headlineLarge,
            modifier = Modifier.padding(bottom = 32.dp)
        )
        
        OutlinedTextField(
            value = username,
            onValueChange = { username = it },
            label = { Text("Username") },
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 16.dp)
        )
        
        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") },
            visualTransformation = PasswordVisualTransformation(),
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 24.dp)
        )
        
        if (state.error.isNotEmpty()) {
            Text(
                state.error,
                color = MaterialTheme.colorScheme.error,
                modifier = Modifier.padding(bottom = 16.dp)
            )
        }
        
        Button(
            onClick = { viewModel.login(username, password) },
            enabled = !state.isLoading,
            modifier = Modifier
                .fillMaxWidth()
                .height(48.dp)
        ) {
            if (state.isLoading) {
                CircularProgressIndicator(
                    color = MaterialTheme.colorScheme.onPrimary,
                    modifier = Modifier.size(24.dp)
                )
            } else {
                Text("Login")
            }
        }
    }
}

class AuthViewModel(
    private val apiService: EngineeringAPI = RetrofitClient.apiService
) : ViewModel() {
    private val _state = MutableStateFlow(AuthState())
    val state = _state.asStateFlow()
    
    fun login(username: String, password: String) {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            try {
                val response = apiService.login(username, password)
                RetrofitClient.setAuthToken(response.access_token)
                _state.update { it.copy(isLoading = false, success = true) }
            } catch (e: Exception) {
                _state.update { it.copy(isLoading = false, error = e.message ?: "Unknown error") }
            }
        }
    }
}

data class AuthState(
    val isLoading: Boolean = false,
    val success: Boolean = false,
    val error: String = ""
)
```

---

## Common Issues & Solutions

### iOS

**Issue:** Connection refused
```swift
// Solution: Ensure URL is correct and API is running
let baseURL = "http://192.168.x.x:8000"  // Use machine IP, not localhost
```

**Issue:** CORS Error
```
// Already fixed in API! All endpoints support CORS
// No changes needed in your iOS app
```

### Android

**Issue:** Cleartext not permitted
```xml
<!-- Add to AndroidManifest.xml for development -->
<domain-config cleartextTrafficPermitted="true">
    <domain includeSubdomains="true">192.168.x.x</domain>
</domain-config>
```

**Issue:** SSL Certificate Error
```kotlin
// For testing only - never use in production!
val client = OkHttpClient.Builder()
    .hostnameVerifier { _, _ -> true }  // Accept all certificates
    .build()
```

---

## Testing Your Mobile Integration

### 1. Test User Registration
```bash
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "mobiletest",
    "password": "test123",
    "full_name": "Mobile Test",
    "role": "mechanic"
  }'
```

### 2. Test Login
```bash
curl -X POST http://localhost:8000/users/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=mobiletest&password=test123"
```

### 3. Test Protected Endpoint
```bash
curl -X GET http://localhost:8000/inventory/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Performance Tips for Mobile

1. **Pagination**: Always use pagination for list endpoints
```
GET /inventory/?skip=0&limit=50
```

2. **Caching**: Cache inventory locally
```kotlin
// Use Room database or SharedPreferences
```

3. **Background Sync**: Queue requests when offline
```kotlin
// Use WorkManager for background tasks
```

4. **Image Optimization**: Compress before uploading
```swift
// Use ImageIO for compression in iOS
```

---

## Resources

- **Swift**: https://swift.org/documentation
- **Kotlin**: https://kotlinlang.org/docs
- **Retrofit**: https://square.github.io/retrofit
- **Alamofire** (iOS): https://github.com/Alamofire/Alamofire
- **Firebase** (for push notifications): https://firebase.google.com

---

**Happy coding! 🎉 Your app is ready for the app stores! 🚀**
