package org.graitdm.edna.ingest;

import java.io.*;
import java.net.URISyntaxException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.stream.Collectors;

import org.apache.http.HttpEntity;
import org.apache.http.client.config.CookieSpecs;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.utils.URIBuilder;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;

/**
 * Performs Ingest using the Twitter v2 API
 * @param <T>
 */
public class TwitterStreamingIngest<T extends Serializable> extends BaseStreamingIngest<T> {

    private final String base_url = "https://api.twitter.com/2/tweets/sample/stream?";
    private Map<String, HashMap<String, Integer>> valid_parameters = new HashMap<>();

    private String bearer_token;
    protected String query_url;
    protected CloseableHttpResponse response;
    protected HttpEntity entity;


    public TwitterStreamingIngest(T serializer, String bearer_token,
                                  List<String> tweet_fields, List<String> user_fields, List<String> media_fields,
                                  List<String> poll_fields, List<String> place_fields) {
        super(serializer);
        this.bearer_token = bearer_token;
        this.query_url = this.buildURL(base_url, tweet_fields, user_fields, media_fields, poll_fields, place_fields);   // TODO add tweet fields etc...
        this.response = null;
        this.buildValidParameters();
    }

    private void buildValidParameters(){

        this.valid_parameters.put("tweet.fields", new HashMap<>(){{
            put("lang",1); put("attachments",1); put("entities",1); put("text",1); put("created_at",1); put("context_annotations",1); put("public_metrics",1); put("in_reply_to_user_id",1); put("withheld",1); put("conversation_id",1); put("author_id",1); put("referenced_tweets",1); put("geo",1); put("id",1); put("possibly_sensitive",1); put("source",1);
        }});
        this.valid_parameters.put("user.fields", new HashMap<>(){{
            put("username",1); put("description",1); put("profile_image_url",1); put("protected",1); put("id",1); put("withheld",1); put("verified",1); put("name",1); put("url",1); put("created_at",1); put("entities",1); put("pinned_tweet_id",1); put("location",1); put("public_metrics",1);
        }});
        this.valid_parameters.put("media.fields", new HashMap<>(){{
            put("width",1); put("height",1); put("media_key",1); put("public_metrics",1); put("preview_image_url",1); put("duration_ms",1); put("type",1);
        }});
        this.valid_parameters.put("poll.fields", new HashMap<>(){{
            put("duration_minutes",1); put("end_datetime",1); put("voting_status",1); put("id",1); put("options",1);
        }});
        this.valid_parameters.put("place.fields", new HashMap<>(){{
            put("contained_within",1); put("country_code",1); put("full_name",1); put("country",1); put("geo",1); put("id",1); put("place_type",1); put("name",1);
        }});

    }

    /**
     * buildURL takes in the base_url and the set of fields to get for each of the parent object models of a tweet
     * and returns a valid url that will stream these tweet objects. If all fields are empty, then the base_url
     * is used, which returns only the tweet-id and the tweet-text
     * @param base_url :
     * @param tweet_fields
     * @param user_fields
     * @param media_fields
     * @param poll_fields
     * @param place_fields
     * @return
     */
    private String buildURL(String base_url, List<String> tweet_fields, List<String> user_fields, List<String> media_fields,
                            List<String> poll_fields, List<String> place_fields){


        String tweet_query = this.buildQuery("tweet.fields", tweet_fields);

        int query_length = tweet_query.length();
        if(query_length > 0) {
            Map<String, String> request_params = new HashMap<>();
            request_params.put("tweet.fields", tweet_query);
            String encoded_url =request_params.keySet()
                    .stream()
                    .map(key -> key+"="+this.encodeValue(request_params.get(key)))
                    .collect(Collectors.joining("&", this.base_url, ""));
            return encoded_url;
        }
        else{   //Empty params. We just use the base url without '?'
            return this.base_url.substring(0,this.base_url.length()-1);
        }
    }
    private String encodeValue(String value)  {
        try {
            return URLEncoder.encode(value, StandardCharsets.UTF_8.toString());
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }
        return "id";    // This is the default return because each Object Model in Tweet has `id`.
    }

    /**
     * buildQuery returns a proper URL query for a given query_field and query_paraams containing a list of tweet fields
     * to get. The list is joined with a comma, i.e. ["id", "name"] becomes "id,name"
     * @param query_field
     * @param query_params
     * @return
     */
    private String buildQuery(String query_field, List<String> query_params){
        query_params = this.verifyQueryParams(query_field, query_params);
        return String.join(",", query_params);
    }

    /**
     * Verifies whether the parameters of a field are valid, using the internally recorded dictionary of valid parameters
     * @param query_params
     * @return
     */
    private List<String> verifyQueryParams(String query_field, List<String> query_params){
        query_params.removeIf(b -> !this.valid_parameters.get(query_field).containsKey(b));
        return query_params;
    }


    /**
     * Returns an iterator over elements of type {@code T}.
     *
     * @return an Iterator.
     */
    @Override
    public Iterator<T> iterator() {
        return new TwitterStreamingIterator<>();
    }

    private class TwitterStreamingIterator<T extends Serializable> implements Iterator<T>{
        private boolean running = false;
        private BufferedReader reader;
        /**
         * Returns {@code true} if the iteration has more elements.
         * (In other words, returns {@code true} if {@link #next} would
         * return an element rather than throwing an exception.)
         *
         * @return {@code true} if the iteration has more elements
         */
        @Override
        public boolean hasNext() {
            return true;    // Twitter stream always has next
        }

        /**
         * Returns the next element in the iteration.
         *
         * @return the next element in the iteration
         * @throws NoSuchElementException if the iteration has no more elements
         */
        @Override
        public T next() {
            if(!this.running){
                // Open the stream
                try {
                    TwitterStreamingIngest.this.response = this.connectStream();
                    TwitterStreamingIngest.this.entity = TwitterStreamingIngest.this.response.getEntity();
                    this.reader = new BufferedReader(new InputStreamReader(TwitterStreamingIngest.this.entity.getContent()));
                    this.reader.readLine();
                    this.running = true;

                } catch (URISyntaxException | IOException e) {
                    e.printStackTrace();
                }
            }

            try {
                TwitterStreamingIngest.this.serializer.
                return this.reader.readLine();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        private CloseableHttpResponse connectStream() throws URISyntaxException, IOException {
            CloseableHttpClient httpClient = HttpClients.custom()
                    .setDefaultRequestConfig(RequestConfig.custom()
                    .setCookieSpec(CookieSpecs.STANDARD).build())
                    .build();
            URIBuilder uriBuilder = new URIBuilder(TwitterStreamingIngest.this.query_url);
            HttpGet httpGet = new HttpGet(uriBuilder.build());
            httpGet.setHeader("Authorization", String.format("Bearer %s", TwitterStreamingIngest.this.bearer_token));
            return httpClient.execute(httpGet);


        }
    }
}
