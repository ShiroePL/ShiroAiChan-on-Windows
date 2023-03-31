import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import android.content.Intent
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import java.io.File
import java.util.Locale
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import okhttp3.ResponseBody
import android.media.MediaPlayer
import com.example.myapplication.R
import com.example.myapplication.databinding.FragmentFirstBinding


class FirstFragment : Fragment() {
    companion object {
        private const val AUDIO_PERMISSION_REQUEST_CODE = 1
    }
    private var _binding: FragmentFirstBinding? = null
    private val binding get() = _binding!!

    // Your existing functionality from MainActivity
    // ...


    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        _binding = FragmentFirstBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Move your code from MainActivity's onCreate method here
        // Replace findViewById calls with view.findViewById
        // ...
        // Access views using binding instead of findViewById
        //binding.textviewFirst.text = "First Fragment"  - example of binding


        val askButton = view.findViewById<Button>(R.id.askbuttonn)
        val questioninput = view.findViewById<EditText>(R.id.questioninput)
        val answeroutput = view.findViewById<TextView>(R.id.answeroutput)
        val voiceInputButton = view.findViewById<Button>(R.id.voice_input_button)

        voiceInputButton.setOnClickListener {
            requestAudioPermission()
        }

        askButton.setOnClickListener {
            val questionText = questioninput.text.toString()
            val usernameText = view.findViewById<EditText>(R.id.username_input).text.toString()

            if (questionText.isNotEmpty() && usernameText.isNotEmpty()) {
                val apiService = createApiService()
                CoroutineScope(Dispatchers.IO).launch {
                    val response: Response<Map<String, String>> = apiService.postQuestion(QuestionWithUser(questionText, usernameText))

                    if (response.isSuccessful) {
                        val answer = response.body()?.get("answer")
                        if (answer != null) {
                            withContext(Dispatchers.Main) {
                                answeroutput.text = answer
                                questioninput.setText("") // Clear the input text
                            }
                        }
                        // Download and play the audio file
                        CoroutineScope(Dispatchers.IO).launch {
                            val audioFile = downloadAudioFile("response.wav")
                            if (audioFile != null) {
                                withContext(Dispatchers.Main) {
                                    playAudioFile(audioFile)
                                }
                            }
                        }

                    } else {
                        withContext(Dispatchers.Main) {
                            answeroutput.text = "Error: ${response.errorBody()?.string()}"
                        }
                    }
                }
            } else {
                answeroutput.text = "Please enter a valid question and username"
            }
        }
    }

    // Move the methods from the onViewCreated method to the class level
    // ...

    private fun requestAudioPermission() {
        if (ContextCompat.checkSelfPermission(requireContext(), Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(requireActivity(), arrayOf(Manifest.permission.RECORD_AUDIO), AUDIO_PERMISSION_REQUEST_CODE)
        } else {
            startSpeechRecognition()
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<String>, grantResults: IntArray) {
        when (requestCode) {
            AUDIO_PERMISSION_REQUEST_CODE -> {
                if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    startSpeechRecognition()
                } else {
                    // Show a message that the permission was not granted
                    Toast.makeText(requireContext(), "Permission to record audio is required", Toast.LENGTH_SHORT).show()
                }
            }
            else -> {
                super.onRequestPermissionsResult(requestCode, permissions, grantResults)
            }
        }
    }

    private fun createApiService(): ApiService {
        val retrofit = Retrofit.Builder()
            .baseUrl("http://10.147.17.21:8000")
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        return retrofit.create(ApiService::class.java)
    }

    private fun startSpeechRecognition() {
        val speechRecognizer = SpeechRecognizer.createSpeechRecognizer(requireContext())
        val speechRecognizerIntent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
        }

        // Set the recognition listener here
        // ...

    }

    private suspend fun downloadAudioFile(audioFileName: String): File? {
        val response = createApiService().getAudio(audioFileName)

        return if (response.isSuccessful) {
            val file = File.createTempFile("audio", ".mp3", requireActivity().cacheDir)
            file.writeBytes(response.body()?.bytes() ?: return null)
            file
        } else {
            null
        }
    }

    private fun playAudioFile(file: File) {
        val mediaPlayer = MediaPlayer().apply {
            setDataSource(file.absolutePath)
            prepare()
            start()
        }
    }
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }


}

data class QuestionWithUser(
    val question: String,
    val username: String
)


interface ApiService {

    @POST("question")
    suspend fun postQuestion(@Body questionWithUser: QuestionWithUser): Response<Map<String, String>>

    @GET("audio/{audio_file_name}")
    suspend fun getAudio(@Path("audio_file_name") audioFileName: String): Response<ResponseBody>

}
