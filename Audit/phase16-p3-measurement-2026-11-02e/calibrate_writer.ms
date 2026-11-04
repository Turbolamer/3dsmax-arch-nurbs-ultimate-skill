-- Minimal unverified writer calibration. No Max geometry/scene reads or edits.
-- Main supplies P3MeasurementOutput = exact NEW absolute local filename.
-- Re-run same filename should refuse without overwriting. No directories/deletes.
(
    global P3MeasurementOutput
    local outputPath = undefined
    local outputStream = undefined
    local outputWriter = undefined
    local hashProvider = undefined
    local outputCreated = false
    local answer = undefined
    local started = timeStamp()
    -- Non-ASCII text checks GetByteCount versus UTF-8 bytes, not UTF-16 length.
    local text = "{\"calibration\":\"AéЖ\",\"line\":\"one\\ntwo\"}"
    fn quoted value =
    (
        local s = substituteString (value as string) "\\" "\\\\"
        s = substituteString s "\"" "\\\""
        s = substituteString s "\n" "\\n"
        s = substituteString s "\r" "\\r"
        s = substituteString s "\t" "\\t"
        "\"" + s + "\""
    )
    fn integerValue value =
    (
        if (classOf value) != Integer and (classOf value) != Integer64 do throw "JSON integer requires Integer/Integer64"
        local s = value as string
        if s.count > 0 and (toLower (substring s s.count 1)) == "l" do s = substring s 1 (s.count - 1)
        if s.count == 0 do throw "Empty JSON integer"
        local firstDigit = if (substring s 1 1) == "-" then 2 else 1
        if firstDigit > s.count do throw "Missing JSON integer digits"
        for i = firstDigit to s.count do if (findString "0123456789" (substring s i 1)) == undefined do throw "Invalid JSON integer token"
        if s.count > firstDigit and (substring s firstDigit 1) == "0" do throw "Leading zero in JSON integer"
        s
    )
    try
    (
        if (integerValue (3516 as Integer64)) != "3516" do throw "Integer64 JSON suffix control failed"
        if (integerValue ((-3516) as Integer64)) != "-3516" do throw "Negative Integer64 JSON suffix control failed"
        if (classOf P3MeasurementOutput) != String do throw "P3MeasurementOutput must be an absolute filename string"
        outputPath = P3MeasurementOutput
        local pathApi = dotNetClass "System.IO.Path"
        if not (pathApi.IsPathRooted outputPath) do throw "Output path must be absolute"
        if outputPath.count < 4 or (substring outputPath 2 1) != ":" or ((substring outputPath 3 1) != "\\" and (substring outputPath 3 1) != "/") do throw "Output path must be drive-qualified absolute"
        if (findString outputPath "\\\\") == 1 do throw "UNC output refused"
        outputPath = (pathApi.GetFullPath outputPath) as string
        local encoding = dotNetObject "System.Text.UTF8Encoding" false
        local expectedBytes = encoding.GetByteCount text
        if expectedBytes > 2097152 do throw "Output exceeds 2 MiB"
        outputStream = dotNetObject "System.IO.FileStream" outputPath ((dotNetClass "System.IO.FileMode").CreateNew) ((dotNetClass "System.IO.FileAccess").ReadWrite) ((dotNetClass "System.IO.FileShare").None)
        outputCreated = true
        outputWriter = dotNetObject "System.IO.StreamWriter" outputStream encoding
        outputWriter.Write text
        outputWriter.Flush()
        outputStream.Flush()
        local fileBytes = outputStream.Length
        if fileBytes != expectedBytes do throw "UTF-8 byte count differs after flush"
        outputStream.Position = 0
        hashProvider = (dotNetClass "System.Security.Cryptography.SHA256").Create()
        local digest = hashProvider.ComputeHash outputStream
        hashProvider.Dispose(); hashProvider = undefined
        if (classOf digest) != Array or digest.count != 32 do throw "SHA-256 digest is not a 32-byte marshalled array"
        local digits = "0123456789abcdef"
        local hex = ""
        for byteValue in digest do
        (
            if byteValue < 0 or byteValue > 255 do throw "Invalid SHA-256 byte"
            hex += (substring digits ((floor (byteValue / 16.0)) + 1) 1) + (substring digits ((mod byteValue 16) + 1) 1)
        )
        outputWriter.Close(); outputWriter = undefined
        outputStream = undefined
        answer = "{\"status\":\"WRITTEN_NOT_VERIFIED\",\"path\":" + (quoted outputPath) + ",\"sha256\":" + (quoted hex)
        answer += ",\"bytes\":" + (integerValue fileBytes) + ",\"expected_bytes\":" + (integerValue expectedBytes) + ",\"text\":" + (quoted text) + ",\"elapsed_ms\":" + ((timeStamp() - started) as string) + "}"
    )
    catch
    (
        local message = (getCurrentException()) as string
        local cleanup = true
        if hashProvider != undefined do try (hashProvider.Dispose(); hashProvider = undefined) catch (cleanup = false)
        if outputWriter != undefined do try (outputWriter.Close(); outputWriter = undefined) catch (cleanup = false)
        if outputStream != undefined do try (outputStream.Close(); outputStream = undefined) catch (cleanup = false)
        answer = "{\"status\":\"INCOMPLETE\",\"error\":" + (quoted message) + ",\"output_created\":" + (if outputCreated then "true" else "false") + ",\"cleanup_ok\":" + (if cleanup then "true" else "false") + "}"
    )
    answer
)
